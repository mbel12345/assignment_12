import uuid

from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import (
    get_db,
    get_engine,
)
from app.database.database_init import (
    init_db,
)
from app.models.calculation import (
    Calculation,
)
from app.models.user import (
    User,
)
from app.schemas.calculation import (
    CalculationBase,
    CalculationRead,
    CalculationResponse,
    CalculationUpdate,
)
from app.schemas.token import (
    TokenResponse,
)
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.auth.dependencies import (
    get_current_active_user,
)

@asynccontextmanager
async def lifespan(app: FastAPI):

    print('Creating tables...')
    engine = get_engine()
    init_db(engine=engine)
    print('Tables created successfully')
    yield

app = FastAPI(
    title='Calculation API',
    description='API for managing calculations',
    version='1.0.0',
    lifespan=lifespan,
    debug=True,
)

@app.get(
    '/health',
    tags=['health']
)
def read_health():

    return {'status': 'ok'}

@app.post(
    '/users/register',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=['auth'],
)
def register(user_create: UserCreate, db: Session = Depends(get_db)):

    # Register a new user

    user_data = dict(user_create)
    user = User.register(db, user_data)
    db.commit()
    db.refresh(user)
    return user

    # Adding try-catch blocks is not possible since validation is done ahead of time in pydantic

@app.post(
    '/users/login',
    response_model=TokenResponse,
    tags=['auth'],
)
def login_json(user_login: UserLogin, db: Session = Depends(get_db)):

    # Login

    auth_result = User.authenticate(db, user_login.username, user_login.password)
    if auth_result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
            headers={'WWW-Authentication': 'Bearer'},
        )

    user = auth_result['user']
    db.commit()

    expires_at = auth_result.get('expires_at')
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    return TokenResponse(
        access_token=auth_result['access_token'],
        refresh_token=auth_result['refresh_token'],
        token_type="bearer",
        expires_at=expires_at,
        user_id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified=user.is_verified
    )

@app.post(
    '/users/token',
    tags=['auth'],
)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    # Login from form

    auth_result = User.authenticate(db, form_data.username, form_data.password)
    if auth_result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return {
        'access_token': auth_result['access_token'],
        'token_type': 'bearer',
    }

@app.post(
    '/calculations',
    response_model=CalculationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=['calculations'],
)
def create_calculation(
    calculation_data: CalculationBase,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):

    # Compute and persist a calculation

    try:
        new_calc = Calculation.create(
            calculation_type=calculation_data.type,
            user_id=current_user.id,
            inputs=calculation_data.inputs,
        )
        new_calc.result = new_calc.get_result()

        # Persist to DB
        db.add(new_calc)
        db.commit()
        db.refresh(new_calc)
        return new_calc

    except ValueError as e:

        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@app.get(
    '/calculations',
    response_model=list[CalculationRead],
    tags=['calculations'],
)
def list_calculations(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):

    # Get a list of calculations by the current user

    calculations = db.query(Calculation).filter(
        Calculation.user_id == current_user.id,
    ).all()
    return calculations

@app.get(
    '/calculations/{calc_id}',
    response_model=CalculationRead,
    tags=['calculations'],
)
def get_calculation(
    calc_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):

    # Get a specific calc by ID

    try:
        calc_uuid = uuid.UUID(calc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid calculation id format.')

    calc = db.query(Calculation).filter(
        Calculation.id == calc_uuid,
        Calculation.user_id == current_user.id,
    ).first()

    if not calc:
        raise HTTPException(status_code=404, detail='Calculation not found')

    return calc

@app.put(
    '/calculations/{calc_id}',
    response_model=CalculationResponse,
    tags=['calculations'],
)
def update_calculation(
    calc_id: str,
    calculation_update: CalculationUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):

    # Edit / Update a calculation

    try:
        calc_uuid = uuid.UUID(calc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid calculation id format.')

    calc = db.query(Calculation).filter(
        Calculation.id == calc_uuid,
        Calculation.user_id == current_user.id,
    ).first()

    if not calc:
        raise HTTPException(status_code=404, detail='Calculation not found.')

    if calculation_update.inputs is not None:
        calc.inputs = calculation_update.inputs
        calc.result = calc.get_result()
    calc.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(calc)
    return calc

@app.delete(
    '/calculations/{calc_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    response_model = None,
    tags=['calculations'],
)
def delete_calculation(
    calc_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):

    # Delete a calculation

    try:
        calc_uuid = uuid.UUID(calc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid calculation id format.')

    calc = db.query(Calculation).filter(
        Calculation.id == calc_uuid,
        Calculation.user_id == current_user.id,
    ).first()

    if not calc:
        raise HTTPException(status_code=404, detail='Calculation not found.')

    db.delete(calc)
    db.commit()
    return None

if __name__ == '__main__':

    # No coverage because this is a main method
    import uvicorn # pragma: no cover
    uvicorn.run('app.main:app', host='127.0.0.1', port=8001, log_level='info') # pragma: no cover
