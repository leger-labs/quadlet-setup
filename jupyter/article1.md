Jupyter with OpenWebUI code interpreter
10 Mar 2025 • llm
Technical blog post. This is about installing Jupyter, mostly because many of the tutorials in Github are set up as Jupyter notebooks.

The second bit, making it work with OpenWebUI, is partly because there is no documentation on this feature at all! I was motivated by the mystery of it, and it is fun even though I don't think I'll be using it much.

Setting up JupyterLab
Here's the ansible playbook for setting it up. This was a little more complicated than I anticipated, because there's several parts to it.

First, you need miniconda to set up Python environments.

Then, you need to set up a conda environment for jupyterlab. In the jupyterlab conda environment, you'll want to set up nb_conda_kernels, notebook_intelligence. This gives JupyterLab the extensions it needs to integrate with LiteLLM, and manage the conda environments and kernels.

For notebook_intelligence I needed to configure LiteLLM in a very specific fashion. It doesn't want the LiteLLM model name, it wants the name defined under litellm_params/model in the config.yaml, with the provider name included.

Provider: LiteLLM compatible
Model Name: openai/lambda-qwen25-coder-32b-instruct
Base URL: https://litellm.mytailscale.ts.net
API Key: sk-LiteLLM-Master-Key
Then, for each project, you'll set up individual projects and/or tutorials that you have, because they can all depend on different versions of Python. For example, I was interested in letta tutorials.

So I install a letta conda environment with ipykernel:

conda create -n letta python=3.13 ipykernel pip
And then install the letta client according to the requirements:

conda activate letta
pip install -r requirements.txt
Once I've done that, I need to register it as a kernel so that JupyterLab can pick it up:

python -m ipykernel install --user --name=letta --display-name="Python (letta)"
And after selecting that kernel in JupypterLab, I was able to run the notebook and step through it.

Integrating with OpenWebUI
OpenWebUI has two modes that can integrate with Jupyter – code execution, which allows the UI to add a "run this" button which runs directly in the browser, and code interpreter, which allows the LLM to execute code, usually for the purposes of generating graphs for exploratory data analysis.

From the admin interface, you go to "Code Execution" and then enable "Enable Code Interpreter" and fill out everything, not forgetting to click the "Save" button at the bottom right corner of the screen.

code interpreter

The main difference between code interpreter and code execution is the code execution is sandboxed and isolated, but in the interpreter, Open WebUI maintains context between code blocks. This means that you can pull in a CSV file in one code block, visualize it in another code block, and keep going.

So in a Jupyter notebook, you first install pandas in your kernel:

%conda install pandas
Bounce the kernel. Then tell OpenWebUI to import some CSV. You will want a reasonably powerful model, enough to understand the context.

Import the following as CSV:

customer_id,purchase_date,product_category,amount,age
1001,2024-09-15,Electronics,899.99,32
1002,2024-09-16,Clothing,129.50,45
1003,2024-09-16,Electronics,1299.99,28
1004,2024-09-17,Home,459.75,52
It should produce something like:

import pandas as pd
from io import StringIO

# Define the CSV data
csv_data = """
customer_id,purchase_date,product_category,amount,age
1001,2024-09-15,Electronics,899.99,32
1002,2024-09-16,Clothing,129.50,45
1003,2024-09-16,Electronics,1299.99,28
1004,2024-09-17,Home,459.75,52
"""

# Read the CSV data into a pandas DataFrame
df = pd.read_csv(StringIO(csv_data))

# Print the resulting DataFrame
print(df)
Then ask it "Using df, please show me the average purchase amount by product category." It'll generate the following code:

# Calculate the average purchase amount by product category
avg_amount_by_category = df.groupby('product_category')['amount'].mean().reset_index()

# Print the result
print(avg_amount_by_category)
and then it will take the raw output, which is:

product_category amount 
0 Clothing 129.50
1 Electronics 1099.99 
2 Home 459.75
and give you the analysis you asked for.

That's basically it! You can now have OpenWebUI automatically run code it generated for you.

Caveats
Because the LLM is both generating and running the code, you have to really trust what it's doing, and put it in a kernel that only has the privileges you want it to have. If you have tools in Jupyter that let it email and buy things from Amazon, there's no guarantee the LLM won't order something or email people.

It can be very powerful, and this guy seems to have enjoyed it.

