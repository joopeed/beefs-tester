#!/usr/bin/python
# coding: utf-8

import popen2, subprocess, socket, os, sys, re, platform, datetime, time


so = platform.system()
	if so == "Linux":
		sep = '/'
	else:
		sep = '\\'
user = "joopeeds"

class Component:
	def __init__(self, name, machine, conf, zipped_path):
        	self.__name = name
		self.__machine = machine
		self.__conf = openconf(conf)
		self.__zipped_path = zipped_path 


	def name(self):
        	return self.__name

	def conf(self):
        	return self.__conf

	def machine(self):
        	return self.__machine

	def execute(remote_command, machine_addr, delay=None):
    		process = subprocess.Popen(" ".join(["ssh",
	                                 user +"@" + machine_addr,
                                         remote_command]),
					 shell=True,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT)
   		out, err = process.communicate()
    		return out, err, process.returncode

	def copy_zip(self,  machine):
		# Copy the zip from the path given in test_config.conf
        	remote_path = user+"@" + machine + ":/tmp/"
        	getdata_cmd = " ".join(["scp", "-r",
        	                        zipped_path,
        	                        remote_path])
		self.__zipped = self.__zipped_path.split(sep)[-1]
        	process = subprocess.Popen(getdata_cmd,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        	out, err = process.communicate()
        	return out, err, process.returncode

	def copy_files(self,  machine, src_path, dest_path):
		# Copy files from a path in this computer to a remote destination
        	remote_path = user+"@" + machine + ":/"+dest_path
        	getdata_cmd = " ".join(["scp", "-r",
        	                        src_path,
        	                        remote_path])
        	process = subprocess.Popen(getdata_cmd,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        	out, err = process.communicate()
        	return out, err, process.returncode

    	def mount():
		# Copy BeeFS zip
		copy_zip(machine())
		# Unzip the files of BeeFS
		execute("unzip /tmp/"+self.__zipped, machine())
		# Remove the zip, already unzipped
		execute("rm /tmp/"+self.__zipped, machine())
		# Copy the configuration file of component in remote machine that will run it
		copy_files(machine(), self.conf, "tmp/"+self.__zipped+"/conf/"+name+".conf")
		
		if name is "honeycomb":
			execute("mkdir "+conf["contributing_storage.directory"], machine())
		else if name is "honeybee":
			execute("mkdir "+conf["mount_directory"], machine())
		
		
	def unmount():
		# removing the directory that contains BeeFS main files
		execute("rm -r /tmp/"+self.__zipped, machine())
		clear()

	def clear():
		# Cleaning metadata of component to start a new test
		if name is "queenbee":
			execute("rm "+conf["metadata_directory"]+"/Queenbee.*", machine())
		if name is "honeycomb":
			execute("rm "+conf["contributing_storage.directory"]+"/*", machine())
			execute("rm "+conf["metadata_directory"]+"/Honeycomb.*", machine())
		
	
	def start():
		def componentisrunning(self):
        		out, err, rcod = execute("ps xau | grep " + 
                              	   	name() + 
                                 	 " | grep -v grep", machine())
      		        return out #if it is running, out is not empty, so it's is true

		# try to start component and return whether it is running or not
		execute("bash /tmp/"+self.__zipped+"/bin/beefs start "+name, machine())
		return componentisrunning()

	def stop():
		def componentisrunning(self):
        		out, err, rcod = execute("ps xau | grep " + 
                              	   	name() + 
                                 	 " | grep -v grep", machine())
      		        return out #if it is running, out is not empty, so it's is true

		# try to stop component and return whether it is running or not
		execute("bash /tmp/"+self.__zipped+"/bin/beefs stop "+name, machine())
		return componentisrunning()


















def openconf(file):

	def fn(line):
 	   if line[0] == "#":
 	       line = ""
 	   else:
 	       idx = re.search (r"[^\\]#", line)
 	       if idx != None:
 	           line = line[:idx.start()+1]
 	   # Split non-comment into key and value.
 	   idx = re.search (r"=", line)
 	   if idx == None:
  	      key = line
  	      val = ""
 	   else:
  	      key = line[:idx.start()]
  	      val = line[idx.start()+1:]
  	  val = val.replace ("\\#", "#")
  	  return (key.strip(),val.strip())

        config = {}
        new = open(file).read()
        for i in new.split('\n'):
                if fn(" "+i)[0]!='':
                        config[fn(" "+i)[0]] = fn(" "+i)[1]
        return config

def opencomponentconf(file):

	def fn(line):
 	   if line[0] == "#":
 	       line = ""
 	   else:
 	       idx = re.search (r"[^\\]#", line)
 	       if idx != None:
 	           line = line[:idx.start()+1]
 	   # Split non-comment into key and value.
 	   idx = re.search (r"=", line)
 	   if idx == None:
  	      key = line
  	      val = ""
 	   else:
  	      key = line[:idx.start()]
  	      val = line[idx.start()+1:]
  	  val = val.replace ("\\#", "#")
  	  return (key.strip(),val.strip())

        config = []
        new = open(file).read().split("[========]")
	zipped_path = new[0]
	for uni in range(1,len(new)):
		config.append({})
        	for i in new[uni].split('\n'):
              	  if fn(" "+i)[0]!='':
                        config[uni][fn(" "+i)[0]] = fn(" "+i)[1]
        return zipped_path, config # returns the zip path that was in header of .conf and a list of dicts containing info confs

def getsize(source):
	folder_size = 0
	for (path, dirs, files) in os.walk(source):
  		for file in files:
    			filename = os.path.join(path, file)
    			folder_size += os.path.getsize(filename)
	return "%.1fMB" % (folder_size/(1024*1024.0))


def generateheader(text):
	return  '#'*((60-len(text+'  '))/2) +' '+ text+' ' + '#'*((60-len(text+'  '))/2) +'\n'


def main():
	

	# this script must be in beefs directory where exists \conf  
	honeybee = openconf('conf'+sep+'honeybee.conf')
	honeycomb = openconf('conf'+sep+'honeycomb.conf')
	source = sys.argv[1] # Type the origem without the last '\'
	if so == "Linux":
		dest = honeybee['mount_directory']
		command = 'cp -r '+source+'/ '+dest+'/\n'
	else: 
		command = 'copy "'+source+'\*.*" "'+dest+'\\" \n'

	queenbee = honeycomb['osdmaster'].split(':')
	if queenbee[0]=="localhost":
		allocation = "Non-Distributed"
	else:
		allocation = "Distributed"
	mode = honeycomb['file_synchronization'] + allocation
	hostname = socket.gethostname()
	size = getsize(source)
	queenbee = honeycomb['osdmaster'].split(':')

	dt = datetime.datetime.now()
	test = ' Test on '+ platform.system() +' '+ dt.strftime("%d/%m/%Y %H:%M ")
	header = '#'*60 + '\n' + generateheader(test) + generateheader("Hostname of honeycomb: "+hostname) + generateheader("Queenbee on "+queenbee[0]) + generateheader("Mode: "+mode) + generateheader("Workload: "+ size)
	log = open('testlogs'+sep+'test.log.'+dt.strftime("%d-%m-%Y.%Hh%M")+'.log','w')
	log.write(header)
	startepoch = int(time.time())
	popen2.popen2(command)[0].readlines()
	endepoch = int(time.time())
	body =  'Copying from '+source+' to '+dest +'\n' + 'Command executed: '+command + '\n' + 'elapsed: ' + str( endepoch - startepoch )  +'s\n' + '#'*60 + '\n'
	log.write(body)
	log.close()


if __name__ == "__main__":

	if len(sys.argv) != 1:
       	   sys.stderr.write("Usage: python beefstester.py config_file\n")
           sys.exit(-1)

	config_file = sys.argv[1]
	#FIXME
	zipped_path, samples_config = opencomponentfile(config_file)
	for sample_config in samples_config: # This things should be in main()
		 samples, queenbee, queenbee_conf, honeycomb, honeycomb_conf, honeybee, honeybee_conf = sample_config.values()
		 data_server = Component("honeycomb", honeycomb, honeycomb_conf, zipped_path)
		 meta_server = Component("queenbee", queenbee, queenbee_conf, zipped_path)
		 client = Component("honeybee", honeybee, honeybee_conf, zipped_path)
	#FIXME
	main(samples_config, zipped_path)



