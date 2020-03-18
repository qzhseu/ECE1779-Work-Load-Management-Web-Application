import os
from managerapp import app

USER_PATH='/Users/qzh/project1779/1779a2/Manager_app'

if __name__=="__main__":
  #  app.run(debug=True, use_reloder=False)
  app.secret_key = "super secret key"
  app.run(port=5010,debug=True)
