#!/usr/bin/python
import os, urllib, shutil, subprocess, sys

copilottunnel_script='https://xXxXxX/copilottunnel.py'
readme='https://xXxXxXxX/README_ONBOARD.txt'
listener_port=0


def checkPort():
	if (int(listener_port) >= 9000) and (int(listener_port) <= 9999):
        	print "Accepted. Using port " + str(listener_port);
		#open('/fileStores/CoPilot/copilot.listener', 'w').write(listener_port)
	else:
        	print "Port incorrect. Exiting...";
        	exit()

def makeDirs():
	if not os.path.exists('/fileStores/CoPilot'):
        	os.makedirs('/fileStores/CoPilot');
	if not os.path.exists('/fileStores/CoPilot/SumoCollector/'):		
		os.makedirs('/fileStores/CoPilot/SumoCollector/');
	print "Created directory structure.";

def downloadScripts():
	files = urllib.URLopener()

	if (files.retrieve(copilottunnel_script, '/fileStores/CoPilot/copilottunnel.py')):
        	print "/fileStores/CoPilot/copilottunnel.py download successful";
	else:
        	print "copilottunnel download failed";
	os.chmod('/fileStores/CoPilot/copilottunnel.py', 0755);
	if (files.retrieve(readme, '/fileStores/CoPilot/README')):
                print "/fileStores/CoPilot/README download successful";

def makePersistent():
	open('/fileStores/CoPilot/copilot.listener', 'w').write(listener_port);
	open('/fileStores/CoPilot/copilot.pid', 'w').write('ThisShowsIfNeverRunBefore');
	open('/fileStores/CoPilot/ps.aux', 'w').write("%s" % subprocess.check_output(['ps','-aux']));

	shutil.copyfile('/opt/3rd_party_int/bin/so_dist.sh', '/opt/3rd_party_int/bin/so_dist.sh.bak');

	if 'python /fileStores/CoPilot/copilottunnel.py quiet_restart' not in open('/opt/3rd_party_int/bin/so_dist.sh', 'r').read():
		with open ('/opt/3rd_party_int/bin/so_dist.sh', 'a') as f:
			f.write('python /fileStores/CoPilot/copilottunnel.py quiet_restart');
                	f.write('');
                	f.close();
	
	with open ('/etc/ssh/sshd_config', 'a') as f:
		f.write('#*******MODIFICATION FOR COPILOT');
		f.write('TCPKeepAlive yes');
		f.close();
	
	#with open ('/etc/ssh/sshd_config', 'a') as f:
	#	f.write('TCPKeepAlive yes');
	#	f.close();
	
	with open ('/root/.ssh/config', 'w') as f:
		f.write('');
		f.close();
	with open ('/root/.ssh/config', 'a') as f:
		f.write('ServerAliveInterval 30');
		f.close();
	with open ('/etc/init.d/rcS', 'a') as f:
		f.write('# CoPilot Tunnel Service');
		f.write('python /etc/init.d/copilottunnel.py quiet_restart');
		f.close();
	print "Added persistence.";

if __name__=="__main__":
	listener_port = sys.argv[1].lower();
	checkPort();
	makeDirs();
	downloadScripts();
	makePersistent();
