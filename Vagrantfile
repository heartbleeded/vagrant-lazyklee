# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.box_version = "14.04"
  config.vm.hostname = 'klee-box'
  config.vm.provision :shell, path: 'klee.sh', keep_color: true, privileged: false
  config.ssh.username = 'vagrant'
  config.vm.network :private_network, ip: "192.168.13.36"
  #config.vm.network "public_network"
  config.ssh.forward_agent = true
  config.vm.synced_folder "sharedFolder", "/home/vagrant/sharedFolder"
  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--memory", "4096"]
    vb.customize ["modifyvm", :id, "--cpus", 4]
    vb.name = "klee-boxx64"
  end
end
