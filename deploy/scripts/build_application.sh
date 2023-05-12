#!/bin/bash

echo "Creating the idea_jet Application"

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

rm -rf /applications/idea_jet/
mkdir /applications/idea_jet/

echo "BUILDING"

workspace_name="idea_jet_${environment}"
jenkins_proj_path="/var/lib/jenkins/workspace/$workspace_name"
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
application_build_path=/applications/idea_jet.tar
python -m venv /applications/idea_jet/venv
. "/applications/idea_jet/venv/bin/activate"
pip install --upgrade pip
pip install wheel
pip install /var/lib/jenkins/workspace/$workspace_name/dist/idea_jet-0.1.0-py3-none-any.whl
echo "Application packages installed into Venv"

echo "Gzipping Application"
tar -czf /tmp/idea_jet.tar /applications/idea_jet/
