Name: Chisthia Khan
ID: 48728470

---Running the Project---

Ensure Python is installed, although available by defaul in the University's server.

1. Open Terminal/Power Shell, connect to a university server with: ssh [student ID]@[ash|iceberg].science.mq.edu.au E.g. connecting to iceberg with an ID of “12345678”: ssh 12345678@iceberg.science.mq.edu.au Enter your OneID password when prompted.


2. Clone the project using command  : git clone https://chisthiakhan007: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@github.com/MQU-COMP8110/comp8110-2025-s2-assignment-2-chisthiakhan007.git 


3. Go insinde the folder using command : cd comp8110-2025-s2-assignment-2-chisthiakhan007

4. In order to check the client.py file with diffrenet configurations individual try running server with: 
  First command :  chmod +x ds-test/ds-server
  Secondcommand :  ./ds-test/ds-server -c ds-test/TestConfigs/config100-short-high.xml

5. Repeat 1 and 3 in another terminal and execute command: python3 client.py. you will see results there.

  _keep changing the confg file (.xml file) to run the client with diffrent configuration
  example: ./ds-test/ds-server -c ds-test/TestConfigs/config100-short-high.xml .

6. Lastly, to run the the auto-script file, use below commands one by one:

1. cd ds-test
2. chmod +x ds_test.py
3. ./ds_test.py -p 50000 -c TestConfigs "python3 ../client.py"

Ruuning the server for step 6 is not necessary


if you ever get that permison is denied to execute the files such as client.py, ds_client.py etc, use this command chmod +x <the file>, then execute the file. When you imtially pull the project from github, you might need to do this for ds-server, client.py and ds_test.py file.
