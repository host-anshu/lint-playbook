# Lint Playbook

A simple tool<sup id="lint-pbook">[1](#ansible-lint)</sup> to check 
<a target="_blank" href="http://docs.ansible.com/ansible/playbooks.html">ansible-playbooks</a> for 
logical consistencies. It uses 
<a target="_blank" href="https://github.com/host-anshu/simpleInterceptor">Simple Interceptor</a> 
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

Implement all of the rules 
<a target="_blank" href="https://github.com/host-anshu/ansible-lint-rules/tree/master/rules">here</a>

___

1. Loosely inspired by 
<a id="ansible-lint" target="_blank" href="https://github.com/willthames/ansible-lint">ansible-lint</a>
