cd demosaurus-webapp
if (($#==0 ));
	then 
	test -f ../Surfdrive/demosaurus.sqlite \
		&& echo "Syncing database from Surfdrive" \
		&& rsync ../data/demosaurus.sqlite instance/demosaurus.sqlite \
		|| ( flask init-db && echo "No database in Surfdrive. Instantiated new database." )
else
 	echo "Not syncing database."
	test -f instance/demosaurus.sqlite && echo "Database exists." || (flask init-db "Instantiated new database.")
fi

export FLASK_APP=demosaurus
export FLASK_ENV=development

flask run
