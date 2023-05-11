#!/bin/bash

echo "Creating the IdeaJet Application"

while getopts ":e:" opt; do
  case $opt in
    e)
      environment=$OPTARG
      ;;
    *)
      echo 'Error in command line parsing' >&2
      exit 1
  esac
done

if [ -z "$environment" ]; then
        echo 'Missing -e' >&2
        exit 1
fi

rm -rf /applications/ideajet/
mkdir /applications/ideajet/

echo "BUILDING"

package_name="${environment}_ideajet"
jenkins_proj_path="/var/lib/jenkins/workspace/$package_name"
JENKINS_VENV_DIR=$jenkins_proj_path/venv 

python -m venv $JENKINS_VENV_DIR
echo "VENV created"
. "${JENKINS_VENV_DIR}/bin/activate"
pip install --upgrade pip
pip install -e $jenkins_proj_path .
pip install wheel
python setup.py bdist_wheel 
deactivate
echo "*** Idea Jet Module Created***"

echo "Building the application"
application_build_path=/applications/ideajet.tar
python -m venv /applications/ideajet/venv
. "/applications/ideajet/venv/bin/activate"
pip install --upgrade pip
pip install wheel
pip install "/var/lib/jenkins/workspace/${package_name}/dist/idea_jet-0.1.0-py3-none-any.whl"
echo "Application packages installed into Venv"

echo "Gzipping Application"
tar -czf /tmp/ideajet.tar /applications/ideajet/
