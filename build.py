import subprocess
import os
import markdown
from jinja2 import Template
from markupsafe import Markup, escape
# Function to build CSS using Tailwind CSS

# Read the template only once
# The template locatio: oxie/src/template.html

# Metadata for the index page, this is a dictionary.
# It is hard coded here for now, because this generator is for a single blog only,
# but it can be read from a file or a database.
meta_data = {
    "title": "Puyu Blog",
    "content": "Welcome to my website.",
    "author": "Puyu",
    "date": "2024-07-17",
    "link": ""
}


template = Template(open("src/template.html").read())
index_template = Template(open("src/index.html").read())
Markdown_Extenstions = ['pymdownx.tilde', 'pymdownx.emoji', 'tables', 'meta','footnotes','md_in_html','extra']   

posts = []
pages = []


def build_css():
    subprocess.run(["npm", "run", "build:css"], check=True)


class POST:
    '''
    Class to represent a blog post or page.
    post and page are the same, but there will be in different directories and different areas in index.html. 
    '''
    def __init__(self, md_path, html_path):
        self.md_path = md_path
        self.html_path = html_path
        self.title = None
        self.content = None
        self.date = None
        self.author = None
        self.tags = None
        self.read_time = None
        self.link = None
        self.summary = None

    def parse(self) -> None:
        '''
        Parse the markdown file and extract metadata and content
        '''
        with open(self.md_path, 'r') as md_file:
            # use markupsafe to escape html content 
            # md_content = Markup(md_file.read())
            # md_content = Markup(escape(md_file.read()))
            # not using markupsafe to escape html content for the moment because it will escape the blockquote in markdown. 
            # I will find a way to escape the html content in the future.
            md_content = md_file.read()
            md = markdown.Markdown(extensions = Markdown_Extenstions)
            html_content = md.convert(md_content)
            self.content = html_content
            # get metadata from the md file
            post_meta_data = md.Meta
            # get the link for page and post domain name + html path
            self.link = meta_data["link"] + self.html_path[4:]
            try: 
                self.title = post_meta_data["title"][0]
                self.author = post_meta_data["authors"][0]
                self.summary = post_meta_data["summary"][0]
                self.date = post_meta_data["date"][0]

            except KeyError:
                print(f"Metadata not found in {self.md_path}")
                pass

        
        
    def render(self) -> None:
        ''' Render the post to HTML
        '''
        rendered_html = template.render(
            title=self.title,
            author=self.author,
            summary=self.summary,
            date=self.date,
            content=self.content,
        )
        with open(self.html_path, "w") as html_file:
            html_file.write(rendered_html)
    

class INDEX:
    '''
    Class to represent the index page
    '''
    def __init__(self, meta_data, posts, pages) -> None:
        '''
        Initialize the index page, read meta data (dictionary) and HTML directory (list of string)
        '''
        self.meta_data = meta_data
        self.posts = posts
        self.pages = pages

    def render(self) -> None:
        '''
        Render the index page
        '''
        rendered_html = index_template.render(
            title=self.meta_data["title"],
            author=self.meta_data["author"],
            date=self.meta_data["date"],
            content=self.meta_data["content"],
            posts=self.posts,
            pages=self.pages
        )
        with open("docs/index.html", "w") as html_file:
            html_file.write(rendered_html)

# Function to convert Markdown files to HTML
def generate_html() -> None:
    '''
    Generate HTML files from Markdown files,
    only for files in source/page and source/post, does not include index.md
    to the docs directory
    '''
    directories = ["source/page", "source/post"]

    for directory in directories:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".md"):
                    md_path = os.path.join(root, file)
                    html_path = os.path.join("docs", os.path.relpath(md_path, "source")).replace(".md", ".html")
                    os.makedirs(os.path.dirname(html_path), exist_ok=True)
                    post = POST(md_path, html_path)   
                    post.parse()
                    if directory == "source/post":
                        posts.append(post)
                    else:
                        pages.append(post)
                    post.render()
    # sort the order of posts to show the latest post first
    posts.sort(key=lambda post: (-post.date, post.title))
    index = INDEX(meta_data, posts, pages)
    index.render()
                

def clean_old_files() -> None:
    '''
    Clean old HTML files
    '''
    for root, dirs, files in os.walk("docs"):
        for file in files:
            if file.endswith(".html"):
                os.remove(os.path.join(root, file))
    try:
        os.remove("docs/styles.css")
    except FileNotFoundError:
        pass
    


if __name__ == "__main__":
    clean_old_files()
    generate_html()
    build_css()
