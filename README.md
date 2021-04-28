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

從源檔集合中提取需要在地化的訊息。
```
make babel-extract
```

基於PO模板檔案創建新的翻譯編目：
```
make babel-init locale=en_US
```
> 此指令為測試用途，本專案使用[POEditor]來管理翻譯編目，並透過API將翻譯好的編目下載到*locale*資料夾。

將翻譯編目編譯為二進制MO檔案：
```
make babel-compile locale=en_US
```

## UI
使用[Jinja]模板引擎及[Tailwind CSS]框架。

從源檔案構建*tailwind.css*：
```
make build_tailwind
```

## CSRF保護
遵循[CSRF Prevention Cheat Sheet]實作CSRF保護機制。

當提交表單而CSRF token過期時會重定向至首頁。

[FastAPI]: https://fastapi.tiangolo.com/
[Starlette]: https://www.starlette.io/
[Pydantic]: https://pydantic-docs.helpmanual.io/
[Uvicorn]: https://www.uvicorn.org/
[Babel]: http://babel.pocoo.org/
[Jinja]: https://jinja.palletsprojects.com/
[Tailwind CSS]: https://tailwindcss.com/
[POEditor]: https://poeditor.com/
[CSRF Prevention Cheat Sheet]: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
[db_sms_impl]: https://github.com/ShenTengTu/db_sms_impl
