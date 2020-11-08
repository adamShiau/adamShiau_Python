import paramiko
import logging
import time
import py3lib.QuLogger

class NetSSH():
	def __init__(self, loggername):
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.sshstatus = False
		self.ftpstatus = False
		self.logger = logging.getLogger(loggername)

	def connectSSH(self, ip, port, usr, psswd):
		self.ip = ip
		self.port = port
		self.usr = usr
		self.psswd = psswd
		self.logger.debug("ip = "+str(ip))
		self.logger.debug("port = "+str(port))
		self.logger.debug("usr = "+str(usr))
		self.logger.debug("passwd = "+str(psswd))
		try:
			self.ssh.connect(self.ip, self.port, self.usr, self.psswd)
		except:
			self.logger.error("SSH connection error")
			return False
		else:
			self.sshstatus = True
			return True

	def connectFTP(self):
		if self.sshstatus :
			try:
				self.ftp = self.ssh.open_sftp()
			except:
				self.logger.error("FTP connection error")
				return False
			else:
				self.ftpstatus = True
				return True

	def sendCmd(self, cmd, getpty = False, timedelay = 0):
		if self.sshstatus: 
			# print(cmd)
			self.logger.debug(cmd)
			if getpty:
				stdin, stdout, stderr = self.ssh.exec_command(cmd, get_pty = True)
			else:
				stdin, stdout, stderr = self.ssh.exec_command(cmd)

			# if stdout:
			# 	self.logger.warning("Non empty return")
			# 	for line in stdout:
			# 		self.logger.debug(line)

			if timedelay:
				time.sleep(timedelay)

			return True
		else:
			return False

	def sendQuerry(self, cmd, getpty = False, timedelay = 0):
		if self.sshstatus:
			# print(cmd)
			self.logger.debug(cmd)
			if getpty:
				stdin, stdout, stderr = self.ssh.exec_command(cmd,get_pty = True)
			else:
				stdin, stdout, stderr = self.ssh.exec_command(cmd)

			if timedelay:
				time.sleep(timedelay)

			return stdout
		else:
			self.logger.error("SSH not connectted while Querry")

	def sendQuerryWithError(self, cmd, getpty = False, timedelay = 0):
		if self.sshstatus:
			self.logger.debug(cmd)
			if getpty:
				stdin, stdout, stderr = self.ssh.exec_command(cmd,get_pty = True)
			else:
				stdin, stdout, stderr = self.ssh.exec_command(cmd)

			if timedelay:
				time.sleep(timedelay)

			return stdout, stderr
		else:
			self.logger.error("SSH not connectted while Querry")

	def getFtpFile(self, filename):
		if self.ftpstatus:
			self.ftp.get(filename, filename)

	def putFtpFile(self, filename):
		if self.ftpstatus:
			self.ftp.put(filename, filename)

	def getFtpFilelist(self, filenamelists):
		if self.ftpstatus:
			i = 0
			for fname in filenamelists:
				self.ftp.get(fname, fname)
				i = i + 1
			if i:
				return True
			else:
				self.logger.error("Filename lists empty")

	def rpConnect(self, rpname):
		host = "rp-"+rpname+".local"



if __name__ == '__main__':
    ip = NetSSH("log")
    SSH_connected = ip.connectSSH("rp-F0741F.local", 22, "root", "root")
    if (SSH_connected):
    	print("SSH connected")
    	cmd = "ls cnt.txt"
    	#ip.sendCmd(cmd, False, 0)
    	out = ip.sendQuerry(cmd, False, 0)
    	for line in out:
	    	print(line)

    	FTP_connected = ip.connectFTP()
    	if (FTP_connected):
    		print("FTP connectted")
    		filenamelist = ["cnt.txt"]
    		ip.getFtpFilelist(filenamelist)

