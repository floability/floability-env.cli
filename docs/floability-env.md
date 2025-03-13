# floability-env.cli

To run some computation in distributed fashion, the distributed computing nodes need to be provisioned with proper environment required to run the respective computations. The same is true for the workflow notebook contained in a [Floability](https://github.com/floability/floability-cli/) backpack. A `Floability` structure consists of a manager and one or more worker nodes. An author of a workflow notebook enjoys the freedom in writing code without worrying much about the environmental dependencies for the code to run in a distributed manner.   

We have found that a workflow notebook (the [matrix-multiplication.ipynb](https://github.com/floability/floability-cli/blob/main/example/matrix-multiplication/workflow/matrix-multiplication.ipynb) notebook for example) often contains code where it becomes very complicated to separate the code to be run in distributed (worker) nodes from the code to be run in the manager node. Here comes the `floability-env.cli` to separate the manager and the worker codes as well as figure out the dependencies to run the respective codes. 

launches the jupyter server if not already running
runs the given notebook with the provided kernel
audits the notebook execution with FLINC on user selection
generates the list of dependencies of the audited notebook
