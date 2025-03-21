import unittest
import os
import sys
import shutil
from pathlib import Path
import json
import tempfile
from unittest.mock import patch, MagicMock

# This fixes the import issue when running with unittest
# Get absolute path to the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# Add to Python path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now we can import the build module directly
import build
from build import POST, CATEGORY, BLOG_INDEX, INDEX, clean_old_files, generate_html, collect_static_files


class TestBuild(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for tests
        self.test_dir = tempfile.mkdtemp()
        
        # Create required directories
        os.makedirs(os.path.join(self.test_dir, 'source/post'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'source/page'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'source/image'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'source/static'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'docs'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'src'), exist_ok=True)
        
        # Create sample meta_data.json
        meta_data = {
            "title": "Test Site",
            "author": "Test Author",
            "description": "Test Description",
            "link": "https://example.com",
            "image": "default-image.jpg",
            "phrases": ["Test Phrase 1", "Test Phrase 2"]
        }
        
        with open(os.path.join(self.test_dir, 'src/meta_data.json'), 'w') as f:
            json.dump(meta_data, f)
        
        # Create sample templates
        with open(os.path.join(self.test_dir, 'src/template.html'), 'w') as f:
            f.write("<html><head><title>{{ title }}</title></head><body>{{ content }}</body></html>")
        
        with open(os.path.join(self.test_dir, 'src/index.html'), 'w') as f:
            f.write("<html><head><title>{{ title }}</title></head><body>{{ content }}</body></html>")
        
        with open(os.path.join(self.test_dir, 'src/category_template.html'), 'w') as f:
            f.write("<html><head><title>{{ category }}</title></head><body>Category: {{ category }}</body></html>")
        
        with open(os.path.join(self.test_dir, 'src/blog_template.html'), 'w') as f:
            f.write("<html><head><title>Blog</title></head><body>Blog content</body></html>")
        
        # Create a sample markdown file
        post_content = """---
title: Test Post
authors: Test Author
date: 2024-01-01
category: test
tags: test, unit-test
summary: This is a test post
last_modified: 2024-01-02
image: test-image.jpg
---

# Test Header

This is a test post content.
"""
        
        with open(os.path.join(self.test_dir, 'source/post/test-post.md'), 'w') as f:
            f.write(post_content)
        
        with open(os.path.join(self.test_dir, 'source/page/test-page.md'), 'w') as f:
            f.write(post_content)
        
        with open(os.path.join(self.test_dir, 'source/index.md'), 'w') as f:
            f.write(post_content)
        
        # Create test image file
        with open(os.path.join(self.test_dir, 'source/image/test-image.jpg'), 'w') as f:
            f.write("test image content")
            
        # Save the original working directory
        self.original_cwd = os.getcwd()
        
        # Change to the test directory
        os.chdir(self.test_dir)
        
        # Back up and modify global variables
        self.original_meta_data = build.meta_data
        self.original_posts = build.posts
        self.original_pages = build.pages
        self.original_categories = build.categories
        
        # Load test meta data using with statement to ensure file is closed
        with open('src/meta_data.json', 'r') as f:
            build.meta_data = json.load(f)
        
        # Reload the templates using with statements
        with open('src/template.html', 'r') as f:
            build.template = build.Template(f.read())
        with open('src/index.html', 'r') as f:
            build.index_template = build.Template(f.read())
        with open('src/category_template.html', 'r') as f:
            build.category_template = build.Template(f.read())
        with open('src/blog_template.html', 'r') as f:
            build.blog_index_template = build.Template(f.read())
        
        # Reset lists
        build.posts = []
        build.pages = []
        build.categories = []

    def tearDown(self):
        """Clean up after each test."""
        # Restore original variables
        build.meta_data = self.original_meta_data
        build.posts = self.original_posts
        build.pages = self.original_pages
        build.categories = self.original_categories
        
        # Change back to the original working directory
        os.chdir(self.original_cwd)
        
        # Remove the test directory
        shutil.rmtree(self.test_dir)

    def test_post_init(self):
        """Test POST class initialization."""
        post = POST('source/post/test-post.md', 'docs/test-post.html')
        self.assertEqual(post.md_path, 'source/post/test-post.md')
        self.assertEqual(post.html_path, 'docs/test-post.html')
        self.assertEqual(post.image, build.meta_data["image"])

    def test_post_parse(self):
        """Test POST class parse method."""
        post = POST('source/post/test-post.md', 'docs/test-post.html')
        post.parse()
        
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.author, 'Test Author')
        self.assertEqual(post.summary, 'This is a test post')
        self.assertEqual(post.category, 'test')
        self.assertEqual(post.date.strftime('%Y-%m-%d'), '2024-01-01')
        self.assertEqual(post.last_modified.strftime('%Y-%m-%d'), '2024-01-02')
        self.assertEqual(post.image, 'test-image.jpg')
        self.assertEqual(post.tags, ['test', 'unit-test'])
        self.assertEqual(post.link, '/test-post.html')

    def test_post_render(self):
        """Test POST class render method."""
        post = POST('source/post/test-post.md', 'docs/test-post.html')
        post.parse()
        post.render()
        
        # Check if the HTML file was created
        self.assertTrue(os.path.exists('docs/test-post.html'))
        
        # Check content of the HTML file
        with open('docs/test-post.html', 'r') as f:
            content = f.read()
            self.assertIn('<title>Test Post</title>', content)

    def test_category_init(self):
        """Test CATEGORY class initialization."""
        post = POST('source/post/test-post.md', 'docs/test-post.html')
        post.parse()
        category = CATEGORY(build.meta_data, [post], 'test')
        
        self.assertEqual(category.category, 'test')
        self.assertEqual(category.posts, [post])
        self.assertEqual(category.tags, ['test', 'unit-test'])
        self.assertEqual(category.link, 'blog_test.html')
        self.assertEqual(category.count, 1)
        self.assertEqual(category.last_post, post)

    def test_category_render(self):
        """Test CATEGORY class render method."""
        post = POST('source/post/test-post.md', 'docs/test-post.html')
        post.parse()
        category = CATEGORY(build.meta_data, [post], 'test')
        category.render()
        
        # Check if the category file was created
        self.assertTrue(os.path.exists('docs/blog_test.html'))
        
        # Check content of the category file
        with open('docs/blog_test.html', 'r') as f:
            content = f.read()
            self.assertIn('<title>test</title>', content)

    @patch('build.subprocess.run')
    def test_build_css(self, mock_run):
        """Test build_css function."""
        build.build_css()
        mock_run.assert_called_once_with(["npm", "run", "build:css"], check=True)

    def test_clean_old_files(self):
        """Test clean_old_files function."""
        # Create some files to be cleaned
        os.makedirs('docs/subdir', exist_ok=True)
        with open('docs/test.html', 'w') as f:
            f.write('Test HTML')
        with open('docs/styles.css', 'w') as f:
            f.write('Test CSS')
        os.makedirs('docs/image', exist_ok=True)
        with open('docs/image/test.jpg', 'w') as f:
            f.write('Test Image')
        
        clean_old_files()
        
        # Check if files were removed
        self.assertFalse(os.path.exists('docs/test.html'))
        self.assertFalse(os.path.exists('docs/styles.css'))
        self.assertFalse(os.path.exists('docs/image/test.jpg'))
        self.assertFalse(os.path.exists('docs/image'))

    def test_collect_static_files(self):
        """Test collect_static_files function."""
        # Ensure target directories don't exist yet
        if os.path.exists('docs/image'):
            shutil.rmtree('docs/image')
        if os.path.exists('docs/page'):
            shutil.rmtree('docs/page')
        
        collect_static_files({
            'source/image': 'docs/image',
            'source/static': 'docs/page'
        })
        
        # Check if files were copied
        self.assertTrue(os.path.exists('docs/image/test-image.jpg'))
        
        # Check content of copied files
        with open('docs/image/test-image.jpg', 'r') as f:
            content = f.read()
            self.assertEqual(content, 'test image content')

    @patch('build.build_css')
    def test_generate_html(self, mock_build_css):
        """Test generate_html function."""
        generate_html()
        
        # Check if HTML files were created
        self.assertTrue(os.path.exists('docs/post/test-post.html'))
        self.assertTrue(os.path.exists('docs/page/test-page.html'))
        self.assertTrue(os.path.exists('docs/blog_test.html'))
        self.assertTrue(os.path.exists('docs/blog_index.html'))
        self.assertTrue(os.path.exists('docs/index.html'))
        
        # Check if posts, pages and categories were populated
        self.assertEqual(len(build.posts), 1)
        self.assertEqual(len(build.pages), 1)
        self.assertEqual(len(build.categories), 1)

    def test_blog_index(self):
        """Test BLOG_INDEX class."""
        post = POST('source/post/test-post.md', 'docs/test-post.html')
        post.parse()
        build.posts = [post]
        
        blog_index = BLOG_INDEX(build.meta_data, build.posts)
        self.assertEqual(blog_index.category_list, {'test'})
        self.assertEqual(blog_index.tags, {'test', 'unit-test'})
        
        blog_index.render()
        
        # Check if blog index file was created
        self.assertTrue(os.path.exists('docs/blog_index.html'))
        
        # Check if category file was created
        self.assertTrue(os.path.exists('docs/blog_test.html'))

    def test_index(self):
        """Test INDEX class."""
        post = POST('source/post/test-post.md', 'docs/test-post.html')
        post.parse()
        page = POST('source/page/test-page.md', 'docs/test-page.html')
        page.parse()
        
        build.posts = [post]
        build.pages = [page]
        
        index = INDEX(build.meta_data, build.posts, build.pages)
        index.parse()
        
        # Check if meta data was updated
        self.assertEqual(build.meta_data['title'], 'Test Post')
        
        index.render()
        
        # Check if index file was created
        self.assertTrue(os.path.exists('docs/index.html'))
        
        # Check content of index file
        with open('docs/index.html', 'r') as f:
            content = f.read()
            self.assertIn('<title>Test Post</title>', content)


if __name__ == '__main__':
    unittest.main()