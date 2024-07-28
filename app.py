from flask import Flask, request, render_template,request,session

import requests
import numpy as np

import pandas as pd

import pickle

import mysql.connector
app=Flask(__name__)
app.secret_key = "abc"
con=mysql.connector.connect(user="root",password="",database="foot")
c=con.cursor()


model = pickle.load(open('artifacts/model.pkl','rb'))
book_names = pickle.load(open('artifacts/book_names.pkl','rb'))
final_rating = pickle.load(open('artifacts/final_rating.pkl','rb'))
book_pivot = pickle.load(open('artifacts/book_pivot.pkl','rb'))



# function to fetch book poster
@app.route("/")
def root():
  return render_template("index.html")

@app.route("/about")
def about():
  return render_template("about.html")

@app.route("/register")
def register():
  return render_template("register.html")


@app.route("/logout")
def logout():
  return render_template("index.html")



def fetch_poster(suggestion):
    book_name = []
    ids_index = []
    poster_url = []

    for book_id in suggestion:
        book_name.append(book_pivot.index[book_id])

    for name in book_name[0]: 
        ids = np.where(final_rating['title'] == name)[0][0]
        ids_index.append(ids)

    for idx in ids_index:
        url = final_rating.iloc[idx]['image_url']
        poster_url.append(url)

    return poster_url




# function to get recommended book

def recommend_book(book_name):
    books_list = []
    book_id = np.where(book_pivot.index == book_name)[0][0]
    distance, suggestion = model.kneighbors(book_pivot.iloc[book_id,:].values.reshape(1,-1), n_neighbors=6 )

    poster_url = fetch_poster(suggestion)
    
    for i in range(len(suggestion)):
            books = book_pivot.index[suggestion[i]]
            for j in books:
                books_list.append(j)
    return books_list , poster_url       


# home page

@app.route('/')

def home():
   book_list = book_names.tolist()
   return render_template('index.html', book_list=book_list)



# recommendation page

@app.route('/recommend', methods=['POST'])

def recommend():
   book_title = request.form['selected_book']
   recommended_book_titles, recommended_book_posters = recommend_book(book_title)
   selected_book = request.form['selected_book']
   return render_template('prediction.html', book_list=book_names.tolist(),
                          recommended_book_titles=recommended_book_titles,
                          recommended_book_posters=recommended_book_posters,
                          selected_book=selected_book) 



@app.route("/registerDB",methods=['POST'])
def registerDB():
  name=request.form['name']
  phone=request.form['phno']
  mail=request.form['mail']
  pwd=request.form['pwd']
  
  s="insert into users(name,phno,email,password) values('%s','%s','%s','%s')"%(name,phone,mail,pwd)
  print("Sql is ",s)
  c.execute(s)
  con.commit()
  return render_template("index.html",msg="Registered Successfully....")

@app.route("/LoginDB",methods=['POST'])
def LoginDB():
  email=request.form['uname']
  pwd=request.form['pwd']
  c.execute("select * from users where email='%s' and password='%s'"%(email,pwd))
  data=c.fetchall()
  if len(data)>0:
    session['id']=data[0][1]
    book_list = book_names.tolist()
    return render_template("prediction.html", book_list=book_list)
  else:
    return render_template("index.html",msg="Pls Check your Credentials...")

@app.route("/predict")
def predict():
  return render_template("UserHome.html")


if __name__ == '__main__':
   app.run(debug=True)
