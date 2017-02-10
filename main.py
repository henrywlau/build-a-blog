#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import jinja2
import webapp2
import datetime

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    subject = db.StringProperty(required = True)
    blog = db.TextProperty(required=True)
    posted = db.DateTimeProperty(auto_now_add = True)
    date = db.DateProperty(auto_now_add = True)

class blog(Handler):
    # def convertDate(date):
    #     dateArray = date.split('-')
    #     newDateArray = [dateArray[1],dateArray[0],dateArray[2]]
    #     newDate = newDateArray.join('-')
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY posted DESC LIMIT 5")
        dateArray = []
        for blog in blogs:
            newPosted = blog.date.strftime('%b %d %y')
            dateArray.append(newPosted)

        self.render("blog.html", blogs=blogs, dateArray=dateArray)

class newpost(Handler):
    def render_front(self, subject="", blog="", error=""):
        self.render("newpost.html", subject=subject, blog=blog, error=error)

    def get(self):
        self.render_front()

    def post(self):
        subject = self.request.get("subject")
        blog = self.request.get("blog")

        if subject and blog:
            post = Blog(subject = subject, blog = blog)
            post.put()
            self.redirect("/blog/%s" % str(post.key().id()))
            # self.redirect("/blog")
        else:
            error = "We need both a subject and a blog!"
            self.render_front(subject, blog, error)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        # self.response.write(id)
        blog = Blog.get_by_id(int(id))
        t = jinja_env.get_template('viewpost.html')
        content = t.render(blog=blog)

        self.response.write(content)

app = webapp2.WSGIApplication([
    ('/blog', blog), ('/newpost', newpost), webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
