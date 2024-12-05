import subprocess
import os
import markdown
from jinja2 import Template
from markupsafe import Markup, escape
from datetime import datetime
import json
from pathlib import Path
import shutil

# Function to build CSS using Tailwind CSS

# Read the template only once
# The template locatio: oxie/src/template.html

# Metadata for the index page, this is a dictionary.
# The metadata is used in the index.html template.
# The metadata json file is located in oxie/src/meta_data.json

# read the metadata only once from /src/meta_data.json
meta_data_dir = "src/meta_data.json"
meta_data = json.load(open(meta_data_dir))


# read the template only once
template = Template(open("src/template.html").read())
# index template is used to render the index page
index_template = Template(open("src/index.html").read())
# category template is used to render a page for each category
category_template = Template(open("src/category_template.html").read())
# blog index template is used to render the blog index page (for all categories)
blog_index_template = Template(open("src/blog_template.html").read())

Markdown_Extenstions = ['pymdownx.tilde', 'pymdownx.emoji', 'tables', 'meta','footnotes','md_in_html','extra']   

posts = []
pages = []
categories = []

# Directories to collect static files from
# The key is the source directory and the value is the target directory
# The target directory and content will not delete if it exists
collect_dirs = {
    'source/image': 'docs/image',
    'source/static': 'docs',
}


# Function to build CSS using Tailwind CSS
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
        self.category = None
        self.tags = []
        self.read_time = None
        self.link = None
        self.summary = None
        self.full_link = None
        # Image is the cover image for the post, it is a relative path to the image
        # It is used in the category page and the blog index page
        # The default image is the image in the meta_data.json
        self.image = meta_data["image"]
        self.post_meta_data = None

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
            self.post_meta_data = md.Meta
            
            # get the relative link 
            self.link = self.html_path[4:]
            # get the link with domain name
            self.full_link = meta_data["link"] + self.link
            
            try: 
                self.title = self.post_meta_data["title"][0]
                self.author = self.post_meta_data["authors"][0]
                self.summary = self.post_meta_data["summary"][0]
                self.category = self.post_meta_data["category"][0]
                self.date = datetime.strptime(self.post_meta_data["date"][0], '%Y-%m-%d')
                # read metadata for last modified date LastModified is optional
                # the default last modified date is the date of the post
                self.last_modified = datetime.strptime(self.post_meta_data.get("last_modified", [self.date.strftime('%Y-%m-%d')])[0], '%Y-%m-%d')
                print(f"Processing {self.md_path} with last modified date {self.last_modified}")

                # Split comma-separated tags and strip whitespace
                raw_tags = self.post_meta_data.get("tags", [""])[0]
                # get the image from the metadata, if not found use the default image from the meta_data.json
                self.image = self.post_meta_data.get("image", [self.image])[0]
                self.tags = [tag.strip() for tag in raw_tags.split(",") if tag.strip()]
            except KeyError:
                print(f"Metadata not found in {self.md_path}")
                pass

        
        
    def render(self) -> None:
        ''' 
        Render the post to HTML
        '''
        rendered_html = template.render(
            meta_data=meta_data,
            post_meta_data=self.post_meta_data,
            title=self.title,
            author=self.author,
            summary=self.summary,
            category=self.category,
            date=self.date,
            last_modified=self.last_modified,
            content=self.content,
            phrases=meta_data["phrases"],
            image=self.image,
            tags=self.tags,
            link=self.link,
        )
        with open(self.html_path, "w") as html_file:
            html_file.write(rendered_html)

class CATEGORY:
    '''
    Class to represent a category page, render a page for each category
    Also contains a list of all tags for the category
    '''
    def __init__(self, meta_data, posts, category) -> None:
        self.meta_data = meta_data
        self.posts = posts
        self.category = category
        self.tags = [tag for post in self.posts for tag in post.tags]
        self.link = f"blog_{category}.html"
        self.count = len(self.posts)
        self.last_post = self.posts[0]
        
    def render(self) -> None:
        '''
        Render the category page
        '''
        rendered_html = category_template.render(
            title=self.meta_data["title"],
            phrases=self.meta_data["phrases"],
            posts=self.posts,
            category=self.category,
            tags=self.tags
        )
        with open(f"docs/blog_{self.category}.html", "w") as html_file:
            html_file.write(rendered_html)

class BLOG_INDEX:
    '''
    Class to represent the blog index page
    It contains all the posts and has side bar for categories.
    '''
    def __init__(self, meta_data, posts) -> None:
        self.meta_data = meta_data
        self.posts = posts
        self.category_list = set([post.category for post in self.posts])
        # Flatten and collect all valid tags from posts
        self.tags = set([
            tag 
            for post in self.posts 
            for tag in (post.tags if post.tags is not None else [])
        ])
        

    def render(self) -> None:
        '''
        Render the blog index page, render a page for each category
        '''

        for category in self.category_list:
            # Filter posts for current category
            category_posts = [post for post in self.posts if post.category == category]
            category_tags = [tag for post in category_posts for tag in post.tags]
            category = CATEGORY(self.meta_data, category_posts, category)
            category.render()
            categories.append(category)
         
        # Render blog index page for all categories
        
        rendered_html = blog_index_template.render(
            title=self.meta_data["title"],
            phrases=self.meta_data["phrases"],
            categories=categories,
        )
        with open("docs/blog_index.html", "w") as html_file:
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
        self.description = None
        self.content = None
        

    def parse(self) -> None:
        '''
        Parse the index page, index.md in the source directory
        '''
        with open("source/index.md", 'r') as md_file:
            md_content = md_file.read()
            md = markdown.Markdown(extensions = Markdown_Extenstions)
            html_content = md.convert(md_content)
            # get metadata from the md file
            self.post_meta_data = md.Meta
            self.content = html_content
            try:
                self.meta_data["title"] = self.post_meta_data.get("title", ["Untitled"])[0]
                self.meta_data["author"] = self.post_meta_data.get("authors", ["Anonymous"])[0]
                self.meta_data["date"] = datetime.strptime(
                    self.post_meta_data.get("date", [datetime.now().strftime('%Y-%m-%d')])[0], 
                    '%Y-%m-%d'
                )
                self.meta_data["description"] = self.meta_data.get("description", ["No description available"])[0]

            except KeyError:
                print(f"Metadata not found in index.md")

    def render_page_index(self) -> None:
        '''
        Render the page index
        '''
        rendered_html = index_template.render(
            title=self.meta_data["title"],
            author=self.meta_data["author"],
            date=self.meta_data["date"],
            description=self.meta_data["description"],
            phrases=self.meta_data["phrases"],
            content=self.content,
            posts=self.posts,
            pages=self.pages,
        )
        
    def render(self) -> None:
        '''
        Render the index page
        '''
        rendered_html = index_template.render(
            title=self.meta_data["title"],
            author=self.meta_data["author"],
            date=self.meta_data["date"],
            description=self.meta_data["description"],
            phrases=self.meta_data["phrases"],
            content=self.content,
            posts=self.posts,
            pages=self.pages,
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
    source_root = Path("source")
    docs_root = Path("docs")


    for directory in directories:
        dir_path = Path(directory)
        # print the work being done
        print(f"Processing Folder: {dir_path}")
        for md_path in dir_path.rglob('*.md'):
            # Calculate the relative path from the source root
            relative_md_path = md_path.relative_to(source_root)
            # Construct the corresponding HTML path in the docs directory
            html_path = (docs_root / relative_md_path).with_suffix('.html')
            # Ensure the parent directory exists
            html_path.parent.mkdir(parents=True, exist_ok=True)
            # Create and process the POST object
            post = POST(str(md_path), str(html_path))
            post.parse()
            if directory == "source/post":
                posts.append(post)
            else:
                pages.append(post)
            post.render()
    # sort the order of posts to show the latest post first
    posts.sort(key=lambda post: (-post.date.timestamp(), post.title))
    
    blog_index = BLOG_INDEX(meta_data, posts)
    blog_index.render()
    index = INDEX(meta_data, posts, pages)
    index.parse()
    index.render()

                

def clean_old_files() -> None:
    '''
    Clean old HTML files
    '''
    print("Cleaning old files")
    docs_dir = Path("docs")
    # Remove all .html files in docs directory and subdirectories
    for html_file in docs_dir.rglob('*.html'):
        html_file.unlink()
    print("Old files cleaned")
    # Remove styles.css if it exists
    styles_css = docs_dir / "styles.css"
    if styles_css.exists():
        styles_css.unlink()
    print("styles.css removed")
    # Remove image directory if it exists
    images_dir = docs_dir / "image"
    if images_dir.exists():
        for image in images_dir.rglob('*'):
            image.unlink()
        images_dir.rmdir()
        print("images directory removed")


def collect_static_files(static_dirs: dict = None) -> None:
    """
    Collect static files from specified directories without deleting the target directory.

    Args:
        static_dirs (dict): Dictionary mapping source directories to target directories.
                            Defaults to {'source/image': 'docs/image'}.
    """
    if static_dirs is None:
        static_dirs = {'source/image': 'docs/image'}

    for source, target in static_dirs.items():
        source_dir = Path(source)
        target_dir = Path(target)
        print(f"Copying files from {source_dir} to {target_dir}")

        if not source_dir.exists():
            print(f"Source directory {source_dir} does not exist")
            continue

        # Ensure the target directory exists
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            for item in source_dir.iterdir():
                source_item = source_dir / item.name
                target_item = target_dir / item.name

                if source_item.is_dir():
                    # Recursively copy subdirectories
                    shutil.copytree(source_item, target_item, dirs_exist_ok=True)
                else:
                    # Overwrite files if they exist
                    shutil.copy2(source_item, target_item)
            print("Files copied successfully")
        except Exception as e:
            print(f"Error copying files: {e}")
            raise

if __name__ == "__main__":
    clean_old_files()
    generate_html()
    collect_static_files(collect_dirs)
    build_css()
