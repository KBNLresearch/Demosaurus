from demosaurus import create_app

if __name__ == '__main__':
	try:
		with open('config.txt', 'r') as f:
			config = {}
			for line in f:
				if line[0] == '#': continue
				(key, val) = line.split()
				config[key] = val
		assert config['SECRET_KEY']
	except AssertionError:
		prinẗ('No SECRET_KEY in configuration file (config.txt)')
	except (FileNotFoundError, IOError):
		print('No configuration (config.txt) found')

	app = create_app(SECRET_KEY = config['SECRET_KEY'])
	app.run()