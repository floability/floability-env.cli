# floability-env.cli

To run some computation in distributed fashion, the distributed computing nodes need to be provisioned with proper environment required to run the respective computations. The same is true for the workflow notebook contained in a [Floability](https://github.com/floability/floability-cli/) backpack. A `Floability` structure consists of a manager and one or more worker nodes. An author of a workflow notebook enjoys the freedom in writing code without worrying much about the environmental dependencies for the code to run in a distributed manner.   

We have found that a workflow notebook (the [matrix-multiplication.ipynb](https://github.com/floability/floability-cli/blob/main/example/matrix-multiplication/workflow/matrix-multiplication.ipynb) notebook for example) often contains code where it becomes very complicated to separate the code to be run in distributed (worker) nodes from the code to be run in the manager node. Here comes the `floability-env.cli` to separate the manager and the worker codes as well as figure out the dependencies to run the respective codes.  

`floability-env.cli` runs the notebook using its own kernel. It then audits the code by trapping function calls and collects the dependency information. Finally it generates a file named `requirements.txt` including the dependencies. It is also possible to separate the manager-wise dependencies and the worker-wise dependencies by using a Floability command.

**Acknowledgment:** the `floability-env.cli` is built based on the ideas of other existing works [FLINC](https://github.com/depaul-dice/Flinc) and [Sciunit](https://github.com/depaul-dice/sciunit). 
