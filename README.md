# 使用Python FastAPI 實現簡易會員系統 （SMS_impl）
- Local OS: Ubuntu 18.04
- Python : 3.7.9
- dependency menagement: Pipenv

[FastAPI]運行在ASGI server，並整合兩框架： 
- [Starlette]負責Web部份
- [Pydantic]負責資料部分
- ASGI server本專案採用[Uvicorn]

使用Pipenv安裝依賴項（若透過Pipenv建立虛擬環境）：
```
pipenv install
```

或讀取requirements.txt安裝依賴項：
```
pip install -r requirements.txt
```

資料庫規劃參見[db_sms_impl]

## i18n
使用[Babel]來處理 i18n及L10n。

[FastAPI]: https://fastapi.tiangolo.com/
[Starlette]: https://www.starlette.io/
[Pydantic]: https://pydantic-docs.helpmanual.io/
[Uvicorn]: https://www.uvicorn.org/
[Babel]: http://babel.pocoo.org/
[db_sms_impl]: https://github.com/ShenTengTu/db_sms_impl
