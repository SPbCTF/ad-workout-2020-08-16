import base64
import binascii
import os
import tkinter as tk
from functools import partial
from tkinter import messagebox
import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def generate_rand(n=16):
    return binascii.b2a_hex(os.urandom(n)).decode()


class StartPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master

        self.var_content = tk.StringVar()

        tk.Label(self, text="Authorize", bg="lightblue", width="300", height="2", font=("Calibri", 13)).pack()
        tk.Label(self, text="").pack()
        tk.Label(self, text="Input username").pack()
        tk.Entry(self, textvariable=self.var_content).pack()
        tk.Label(self, text="").pack()
        tk.Button(self, text="Auth", height="2", width="30", command=self.auth).pack()

    def auth(self):
        password = self.var_content.get()
        r = requests.post(f"{self.master.server}/auth", data={"password": password}, verify=False)
        if r.status_code == 200:
            self.master._password = password
            self.master.switch_frame(PageProfile)
        else:
            messagebox.showerror("Error", "Cannot auth")


class PageProfile(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        self.master._edit = None
        tk.Label(self, text=f"{master._password}'s profile", bg="lightblue", width="300", height="2",
                 font=("Calibri", 13)).pack()

        tk.Button(self, text="Exit", height="2", width="30", command=lambda: master.switch_frame(StartPage)).pack()
        tk.Button(self, text="New article", height="2", width="30",
                  command=lambda: master.switch_frame(PageArticleEdit)).pack()
        tk.Button(self, text="Discover article", height="2", width="30", command=self.discover).pack()

        tk.Label(self, text=f"Your articles", bg="lightgreen", width="150", height="2", font=("Calibri", 13)).pack()

        frame = tk.Frame(self)
        frame.pack()

        r = requests.post(f"{self.master.server}/listArticles", {"password": master._password}, verify=False)
        if r.status_code != 200:
            messagebox.showerror("Error", "Cannot load articles")
        else:
            master._articles = {}
            for i, article_id in enumerate(r.json()):
                data = requests.post(f"{self.master.server}/loadArticle",
                                     {"password": master._password, "article_id": article_id.rstrip("=")}, verify=False).json()
                master._articles[data["article_id"]] = data
                tk.Label(frame, text=data['title']).grid(row=i, column=0, padx=5, pady=5)
                tk.Button(frame, text="edit", command=partial(lambda x: self.edit(x), data)).grid(row=i, column=1,
                                                                                                  padx=5, pady=5)
                tk.Button(frame, text="view", command=partial(lambda x: self.view(x), data)).grid(row=i, column=2,
                                                                                                  padx=5, pady=5)

    def discover(self):
        self.master.switch_frame(PageDiscover)

    def edit(self, data):
        self.master._edit = data
        self.master.switch_frame(PageArticleEdit)

    def view(self, data):
        self.master._view = data
        self.master.switch_frame(PageViewArticle)


class PageDiscover(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text=f"{master._password}'s profile", bg="lightblue", width="300", height="2",
                 font=("Calibri", 13)).pack()

        tk.Button(self, text="Exit", height="2", width="30", command=lambda: master.switch_frame(StartPage)).pack()
        tk.Button(self, text="Back", height="2", width="30", command=lambda: master.switch_frame(PageProfile)).pack()

        frame = tk.Frame(self)
        frame.pack()
        self.var_tag = tk.StringVar()
        tk.Entry(frame, textvariable=self.var_tag).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(frame, text="Search by tag", command=self.search).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text=f"Discover new articles", bg="lightgreen", width="150", height="2",
                 font=("Calibri", 13)).pack()

        self.articles = requests.get(f"{self.master.server}/listAllArticles", verify=False).json()
        self.keys = [a.split(":", 1)[0] for a in self.articles]
        self.titles = [a.split(":", 1)[1] for a in self.articles]
        for a in master._articles.keys():
            if a not in self.keys:
                messagebox.showerror("Error", "Articles list broken")

        self.listbox = tk.Listbox(self)
        self.listbox.pack()
        for title in self.titles:
            self.listbox.insert(tk.END, title)

    def search(self):
        tag = self.var_tag.get()
        r = requests.post(f"{self.master.server}/search", {"tag": tag}, verify=False)
        if r.status_code != 200:
            messagebox.showerror("Error", f"Not found any article by tag: {tag}")
        else:
            result = r.json()
            found = []
            for article in result["articles"]:
                try:
                    found.append(self.titles[self.keys.index(article)])
                except Exception as e:
                    continue
            if len(found):
                self.listbox.delete(0, tk.END)
                for f in found:
                    self.listbox.insert(tk.END, f)
            else:
                messagebox.showerror("Error", f"Not found any article by tag: {tag}")


class PageArticleEdit(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master

        tk.Label(self, text=f"{master._password}'s profile", bg="lightblue", width="300", height="2",
                 font=("Calibri", 13)).pack()
        tk.Button(self, text="Back", height="2", width="30", command=lambda: master.switch_frame(PageProfile)).pack()

        self.var_title = tk.StringVar()

        tk.Label(self, text="").pack()
        tk.Label(self, text="Title").pack()
        if master._edit is not None:
            tk.Entry(self, textvariable=self.var_title, state='disabled').pack()
        else:
            tk.Entry(self, textvariable=self.var_title).pack()
        tk.Label(self, text="Content").pack()
        self.var_content = tk.Text(self, height=5, borderwidth=2, relief="groove")
        self.var_content.pack()
        tk.Label(self, text="").pack()
        tk.Button(self, text="Save", height="2", width="30", command=self.save).pack()

        if master._edit is not None:
            self.var_title.set(master._edit['title'])
            self.var_content.insert(tk.END, master._edit['content'])

    def save(self):
        title = self.var_title.get()
        content = self.var_content.get("1.0", 'end-1c')

        if len(title) == 0 or len(content) == 0:
            messagebox.showerror("Error", "Title and content cannot be empty")
            return

        if self.master._edit is not None:
            article_id = self.master._edit["article_id"].rstrip("=")
            r = requests.post(f"{self.master.server}/saveArticle",
                              {"password": self.master._password, "content": content, "article_id": article_id}, verify=False)
        else:
            article_id = base64.b64encode(generate_rand().encode()).decode().rstrip("=")
            r = requests.post(f"{self.master.server}/addArticle",
                              {"password": self.master._password, "title": title, "content": content,
                               "article_id": article_id}, verify=False)

        if r.status_code != 200:
            messagebox.showerror("Error", f"Cannot save article: {r.text}")
        else:
            messagebox.showinfo("OK", f"Article saved")


class PageViewArticle(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        tk.Label(self, text=f"{master._password}'s profile", bg="lightblue", width="300", height="2",
                 font=("Calibri", 13)).pack()

        tk.Button(self, text="Back", height="2", width="30", command=lambda: master.switch_frame(PageProfile)).pack()

        tk.Label(self, text=f"{master._view['title']}", bg="lightgreen", width="150", height="2",
                 font=("Calibri", 13)).pack()

        tk.Label(self, text=f"Article {master._view['content']}", width="150", font=("Calibri", 14)).pack()

        frame = tk.Frame(self)
        frame.pack()

        self.var_tag = tk.StringVar()
        self.var_comment = tk.StringVar()

        tk.Entry(frame, textvariable=self.var_tag).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(frame, text="Add new tag", command=self.add_tag).grid(row=0, column=1, padx=5, pady=5)

        tk.Entry(frame, textvariable=self.var_comment).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(frame, text="Add new comment", command=self.add_comment).grid(row=1, column=1, padx=5, pady=5)

        commentsList = requests.post(f"{self.master.server}/getComments", {"password": master._password,
                                                               "article_id": master._view["article_id"].rstrip(
                                                                   "=")}, verify=False).json()

        tk.Label(self, text="Comments", bg="lightgreen", width="150", height="2", font=("Calibri", 13)).pack()
        listbox = tk.Listbox(self)
        listbox.pack()
        for comment in commentsList:
            listbox.insert(tk.END, comment)

    def add_tag(self):
        tag = self.var_tag.get()
        r = requests.post(f"{self.master.server}/tagArticle", {"password": self.master._password, "tag": tag,
                                                   "article_id": self.master._view["article_id"].rstrip("=")}, verify=False)
        if r.status_code == 200:
            messagebox.showinfo("OK", "Tagged")
        else:
            messagebox.showerror("Error", f"Cannot tag article: {r.text}")

    def add_comment(self):
        comment = self.var_comment.get()
        r = requests.post(f"{self.master.server}/addComment", {"password": self.master._password, "comment": comment,
                                                   "article_id": self.master._view["article_id"].rstrip("=")}, verify=False)
        if r.status_code == 200:
            messagebox.showinfo("OK", "Commend saved")
        else:
            messagebox.showerror("Error", f"Cannot add comment to the article: {r.text}")

