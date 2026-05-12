# Test_oauth_physionet_flow

## Testing the OAuth client application
1. In the terminal, run the PhysioNet server on localhost (e.g., port 8000):
```bash
   ./manage.py runserver 8000
```
2. In a separate terminal, run the `test_oauth_physionet_flow` server on a different port (e.g., port 8001):
```bash
   ./manage.py runserver 8001
```
3. In the browser, access `http://localhost:8001/` and click on the PhysioNet logo to log in (or navigate directly to `http://localhost:8001/physionet/login/`)
4. When the app requests permission to **"Read access to user's credentialing and training status"**, click **Authorize**
5. You will see the response for `slug=demoeicu` and `version=2.0.0` (Note that has_access can be true or false depending on the user logged in):
```json
   {
     "status_code": 200,
     "body": {
       "has_access": true,
       "slug": "demoeicu",
       "version": "2.0.0"
     }
   }
```
6. To check access for a different project, navigate to:
`http://localhost:8001/physionet/dataset/?slug=SLUG&version=VERSION`

   For example: `http://localhost:8001/physionet/dataset/?slug=demoselfmanaged&version=1.0.0`
