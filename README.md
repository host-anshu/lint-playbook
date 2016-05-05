# Lint Playbook

A simple tool to check [ansible-playbooks](http://docs.ansible.com/ansible/playbooks.html) for 
logical consistencies. It uses [Simple Interceptor](https://github.com/host-anshu/simpleInterceptor) 
to achieve this.

## Setup

Using pip:

    pip install LintPlaybook==0.1.dev1

From Source:

    git clone https://github.com/host-anshu/lint-playbook
    cd lint-playbook
    python setup.py install

## Usage

    lint-pbook <ansible-playbook options> ex_playbook.yml

## Example

![Linter Output](sample_data/output.jpg?raw=true "Linter Output")

## Roadmap

Implement all of the rules [here](https://github.com/host-anshu/ansible-lint-rules/tree/master/rules).
