# floability-env.cli

This repo is used to capture notebook dependencies and generate the `environment.yml` for it. It is necessary that the notebook uses a single worker running locally.


The user needs to run the following command from the terminal:

` python floability-env-cli.py  --notebook {notebook_path}`

<br>

`floability-env-cli.py` executes the Jupyter notebook and the worker code and audits their execution using `strace`. It then extracts and gathers the dependencies for both worker and manager code into an `environment.yml` file (example shown below): 
<br>
```
name: autoenv
channels:
- defaults
manager-dependencies:
- rich
- matplotlib
- ndcctools
worker-dependencies:
- cloudpickle=3.1.1
- numpy=2.2.4
```

Acknowledgment: The `floability-env.cli` is built based on the ideas of other existing works [FLINC](https://github.com/depaul-dice/Flinc/) and [Sciunit](https://github.com/depaul-dice/sciunit). 
