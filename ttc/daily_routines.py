import camel_care
import ncore_login

def lambda_handler(event, context):
    LOCAL_RUN = event.get("local_run", False)
    ncore_login.login_to_ncore(LOCAL_RUN)
    camel_care.care_camel(LOCAL_RUN)


# For testing purposes when not running on Lambda
if __name__ == "__main__":
    event = {"local_run": True}
    lambda_handler(event, None)
