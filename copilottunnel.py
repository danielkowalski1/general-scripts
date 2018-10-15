#!/usr/bin/python

#
# STORE THIS IN /.ssh/authorized_keys :
# command="netstat -an | grep 0.0.0.0:9003",no-pty ssh-rsa xXxXxXxXxX<PUBLIC-KEY-GOES-HERE> Dan-Comment-Here
#
#from subprocess import Popen, check_output
#from sys import argv
import traceback, sys, subprocess, os

PORT=open('/fileStores/CoPilot/copilot.listener').read()  ##### Modification: Reading listener from file
HOST='xXxXxXxX.com'
KEYFILE='/fileStores/CoPilot/privkey'
LISTENER=open('/fileStores/CoPilot/copilot.listener').read()
PID=open('/fileStores/CoPilot/copilot.pid').read()

open('/fileStores/CoPilot/ps.aux', 'w').write(subprocess.check_output(["ps","-aux"]))

def _start():
	if not os.path.isfile('/root/.ssh/known_hosts'):
		open('/root/.ssh/known_hosts', 'a').write('');
	if "xXxXxXxX.com" not in open('/root/.ssh/known_hosts','r').read():
		add_to_knownHosts = subprocess.Popen(["ssh", HOST, "2> /dev/null"], shell=False);
		add_to_knownHosts.communicate();

	if '%s' % PID in open('/fileStores/CoPilot/ps.aux').read():
		print "Tunnel running...";
		print "PID: %s" % open('/fileStores/CoPilot/copilot.pid', 'r').read();
	else:
		try:
                	print "Starting CoPilot Tunnel...";
			copilot = subprocess.Popen(["ssh", "-i", KEYFILE, "dsm@%s" % HOST, "-N", "-R *:%d:localhost:443" % int(PORT), ">/dev/null &"], shell=False);
			open('/fileStores/CoPilot/copilot.pid', 'w').write("%d" % copilot.pid);
			print "PID: %d" % copilot.pid;
        	except Exception as e:
                	print e;

def _stop(pid):
	if '%s' % PID in open('/fileStores/CoPilot/ps.aux').read():
		print "Stopping tunnel...";
		copilot = subprocess.Popen(["kill", "-9", "%s" % open('/fileStores/CoPilot/copilot.pid', 'r').read()], shell=False);
		print "Killed PID: %s" % open('/fileStores/CoPilot/copilot.pid', 'r').read();
		pid='EMPTY PID';
	else:
		print "Nothing to stop."

def _restart():
	if '%s' % PID in open('/fileStores/CoPilot/ps.aux').read():
                copilot = subprocess.Popen(["kill", "-9", "%s" % open('/fileStores/CoPilot/copilot.pid', 'r').read()], shell=False);
                print "Killed PID: %s" % open('/fileStores/CoPilot/copilot.pid', 'r').read();
		try:
                        copilot = subprocess.Popen(["ssh", "-i", "%s" % KEYFILE, "dsm@%s" % HOST, "-N", "-R *:%d:localhost:443" % int(PORT), ">/dev/null &"], shell=False);
                        open('/fileStores/CoPilot/copilot.pid', 'w').write("%d" % copilot.pid);
			print "New PID: %d" % copilot.pid;
                except Exception as e:
                        print e;
	else:
		print "Nothing to kill. Starting tunnel.";
		try:
                        copilot = subprocess.Popen(["ssh", "-i", "%s" % KEYFILE, "dsm@%s" % HOST, "-N", "-R *:%d:localhost:443" % int(PORT), ">/dev/null &"], shell=False);
                        open('/fileStores/CoPilot/copilot.pid', 'w').write("%d" % copilot.pid);
                        print "New PID: %d" % copilot.pid;
                except Exception as e:
                        print e;

def _quiet_restart():
        if '%s' % PID in open('/fileStores/CoPilot/ps.aux').read():
                copilot = subprocess.Popen(["kill", "-9", "%s" % open('/fileStores/CoPilot/copilot.pid', 'r').read()], shell=False);
                try:
                        copilot = subprocess.Popen(["ssh", "-i", "%s" % KEYFILE, "dsm@%s" % HOST, "-N", "-R *:%d:localhost:443" % int(PORT), ">/dev/null &"], shell=False);
                        open('/fileStores/CoPilot/copilot.pid', 'w').write("%d" % copilot.pid);
                except Exception as e:
                        print e;
        else:
                try:
                        copilot = subprocess.Popen(["ssh", "-i", "%s" % KEYFILE, "dsm@%s" % HOST, "-N", "-R *:%d:localhost:443" % int(PORT), ">/dev/null &"], shell=False);
                        open('/fileStores/CoPilot/copilot.pid', 'w').write("%d" % copilot.pid);
                except Exception as e:
                        print e;

def _status():
	if '%s' % PID in open('/fileStores/CoPilot/ps.aux').read():
		print "Tunnel is running with PID: %s" % open('/fileStores/CoPilot/copilot.pid', 'r').read();
	else:
		print "No tunnel running.";

if __name__=="__main__":
	try:
		arg = sys.argv[1].lower()
		if arg == '':
			print "Usage: copilottunnel.py <start/stop/restart/status>";
		if arg == 'start':
			_start()
		elif arg == 'stop':
			_stop(PID)
		elif arg == 'restart':
			_restart()
		elif arg == 'quiet_restart':
			_quiet_restart()
		elif arg == 'status':
			_status()
		else:
			print "Invalid option. Exiting...";
	except Exception:
		print "Something went wrong. %s" % traceback.format_exc()
