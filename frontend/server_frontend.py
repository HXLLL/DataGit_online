import os
import uuid
import subprocess

import flask
from flask import templating

program_dir = '/home/hxl/Repo/DataGit_online'
tmpdir = os.path.join(program_dir, 'frontend/tmp')
server_cli = ['/usr/bin/python', 
              os.path.join(program_dir, 'server_cli.py'),
             ]
app = flask.Flask(__name__)

@app.route("/")
def index():
    cmd = server_cli + ['get_repo', '-a']
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    result = result.stdout.decode('utf-8')
    repo_list = result.split('\n')
    repo_list = [f'<p><a href="/repo/{s}">{s}</a></p>' for s in repo_list]
    return ('\n'.join(repo_list)).encode('utf-8')


@app.route('/repo/<repo_name>')
def repo_reponame(repo_name):
    cmd = server_cli + ['get_repo', '-r', repo_name]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    return result.stdout

@app.route('/create')
def create():
    return templating.render_template("create.html")


@app.route('/fork')
def fork():
    return templating.render_template("fork.html")


@app.route('/background_process_test')
def background_process_test():
    print ("Hello")
    return ("nothing")


@app.route('/create_repo', methods=['POST'])
def create_repo():
    repo_name = flask.request.form['repo_name']
    file = flask.request.files['key_file']
    filename = os.path.join(tmpdir, str(uuid.uuid4()))
    file.save(filename)
    cmd = server_cli + ['create', repo_name, '--key_file', filename]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    return result.stdout


@app.route('/fork_repo', methods=['POST'])
def fork_repo():
    old_repo = flask.request.form['old_repo']
    new_repo = flask.request.form['new_repo']
    file = flask.request.files['key_file']
    filename = os.path.join(tmpdir, str(uuid.uuid4()))
    file.save(filename)
    cmd = server_cli + ['fork', old_repo, new_repo, '--key_file', filename]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    return result.stdout

if __name__ == '__main__':
    app.run("0.0.0.0",port=8888, debug=True)