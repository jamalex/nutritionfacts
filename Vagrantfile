# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|

  config.vm.box = "ubuntu/xenial64"

  config.vm.network "forwarded_port", guest: 8000, host: 10080

  config.vm.network "private_network", ip: "192.168.33.15"

  config.vm.synced_folder ".", "/data"

  config.vm.provider "virtualbox" do |vb|
    # Customize the amount of memory on the VM:
    vb.memory = "2048"
  end
  #
  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL

    ### install bazel

    apt-get -y install pkg-config zip g++ zlib1g-dev unzip python

    sudo -u ubuntu curl -L https://github.com/bazelbuild/bazel/releases/download/0.8.0/bazel-0.8.0-installer-linux-x86_64.sh -o /home/ubuntu/bazel-installer.sh
    chmod +x /home/ubuntu/bazel-installer.sh
    bash /home/ubuntu/bazel-installer.sh

    ### install and set up postgres
    apt-get -y install postgresql postgresql-contrib
    sudo -u postgres createuser nutritionfacts || true
    sudo -u postgres createdb nutritionfacts -O nutritionfacts || true

    ### install google-cloud-sdk

    export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)"
    echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
    apt-get update && apt-get -y install google-cloud-sdk kubectl


    echo "GCloud SDK installed! Make sure to run gcloud init once you've SSHed."
  SHELL
end
