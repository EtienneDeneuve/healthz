# healthz
Python Api to check the state of a server and return a 200 or 503 pages for Load Balancer

## Dependencies installation
You need to install the required python module using :
```bash
sudo pip install -r requirements.txt
```
## how to use it
First modify the config.yaml to remove checks you don't need, and configure with your values and then launch it using
```bash
# you need to launch it as root as pyping need that
python healtz.py <listening port, not mandatory, if you want 8080>
```
## Exclude file
You can add a file named exclude in the root folder of the script to exclude temporary the server.
