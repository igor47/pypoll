#!/usr/bin/python

from pysqlite2 import dbapi2 as sqlite
import os, os.path, datetime, titlecase, json
import cgi, cgitb

cgitb.enable()

def getDB():
	dbfile = "/var/www/poll/data/poll.db"
	if not os.path.isfile(dbfile):
		con = sqlite.connect(dbfile,detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
		con.execute("create table votes(title text, author text, comments text, useraddr text, added datetime)")
	else:
		con = sqlite.connect(dbfile,detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)

	con.row_factory = sqlite.Row
	con.text_factory = str
	return con

def add(con, form):
	data = (form['author'].title(), titlecase.titlecase(form['title']), form['comments'], os.getenv('REMOTE_ADDR'), datetime.datetime.now())
	con.execute("insert into votes(author, title, comments, useraddr, added) VALUES (?,?,?,?,?)", data)
	con.commit()
	print "Content-type: text/html\n\n"
	print open('thankyou.html').read()

def show(con, form):
	print "Content-type: text/x-json\n\n"
	cur = con.execute("select count(*) as votes, author, title from votes group by author,title order by votes desc, author asc")
	print json.write([{'votes':i[0],'author':i[1],'title':i[2]} for i in cur.fetchall()])

def search(con, form):
	print "Content-type: text/x-json\n\n"
	data = []
	q = "select author, title from votes where 1=1"
	for field in ['author','title']:
		if field not in form: continue
		if len(form[field]) >= 3:
			q += " and %s like ?" % field
			data.append( '%' + form[field] + '%' )
	q += " group by author, title"

	if data == []:
		print json.write([])
	else:
		cur = con.execute(q,tuple(data))
		data = [{'author':i[0],'title':i[1]} for i in cur.fetchall()]
		print json.write(data)

def main():
	form = cgi.FieldStorage(keep_blank_values=True)
	dform = {}
	for key in form:
		dform[key] = form.getfirst(key)
	form = dform

	if 'action' not in form:
		print "Content-type: text/html\n\n"
		print open('poll.html').read()
		return

	con = getDB()
	if form['action'] == 'add':
		add(con,form)
	if form['action'] == 'showresults':
		show(con,form)
	if form['action'] == 'search':
		search(con,form)

if __name__ == '__main__':
	main()
