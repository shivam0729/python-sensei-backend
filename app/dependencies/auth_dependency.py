from fastapi import (
    Depends,
    HTTPException,
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)

from jose import jwt, JWTError
from sqlmodel import Session

from ..db import get_db
from ..models import User
from ..core.config import settings

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):

    try:

        # Extract token
        token = credentials.credentials

        print("TOKEN RECEIVED:", token)

        # Decode token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"],
        )

        print("PAYLOAD:", payload)

        # Extract user id
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload"
            )

        # Fetch user
        user = db.get(User, int(user_id))

        print("USER:", user)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return user

    except JWTError as e:

        print("JWT ERROR:", str(e))

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    except Exception as e:

        print("GENERAL AUTH ERROR:", str(e))

        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )