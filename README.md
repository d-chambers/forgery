# Forgery

This is a simple repo to create a blog post about a fictional circulation test at the UTAH FORGE geothermal site. 

Click [here](https://username.github.io/repo-name/index.html) to see the blog.

To create the post, first [install quarto](https://quarto.org/docs/get-started/) and [uv](https://docs.astral.sh/uv/getting-started/installation/) for your platform. Next, run the following commands:

```bash
# Test the code and ensure everything is installed
uv run pytest  
# Render the blog.
uv run quarto render blog.qmd
# Rename the blog to index.html so it works with gh pages
mv blog.html index.html
```

Then open index.html in your browser of choice. 
