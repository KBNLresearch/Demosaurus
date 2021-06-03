cd demosaurus-webapp
if (($#==0 ));
	then 
	test -f ../data/demosaurus.sqlite \
		&& echo "Syncing database from data dir" \
		&& rsync ../data/demosaurus.sqlite instance/demosaurus.sqlite \
		|| (echo "No database found!") \
	else
 	echo "Not syncing database."
	test -f instance/demosaurus.sqlite && echo "Database exists." || (echo "No database found!")
fi
python3 main.py
