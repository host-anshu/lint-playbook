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
    # either
    python setup.py install
    # or, to install in development mode
    python setup.py develop

## Usage

    lint-pbook <ansible-playbook options> ex_playbook.yml

## Example

For cases when it encounters setup failures:

![Setup Failure](sample_data/setup_failure.jpg?raw=true "Setup Failure")

Otherwise

![Linter Output](sample_data/output.jpg?raw=true "Linter Output")

## Roadmap

Implement all of the rules [here](https://github.com/host-anshu/ansible-lint-rules/tree/master/rules).

## Implemented Rules

Rules that have been implemented(alpha stage) are:

1. [Undefined variable](https://github.com/host-anshu/ansible-lint-rules/blob/master/rules/specs/undefined_vars.feature)
2. [Unused variable](https://github.com/host-anshu/ansible-lint-rules/blob/master/rules/specs/unused_vars.feature)
3. [Conflicting variable](https://github.com/host-anshu/ansible-lint-rules/blob/master/rules/specs/conflicting_vars.feature)
