conf = "/where/you/put/your/conf/files/"
assets_root = "/where/you/put/your/submitted/assets/"
gnupg_home = '/where/you/want/gpg/to/be/'

scripts_home = {
	"python" : '/where/you/put/your/py/scripts/'
}

file_salt = "YOU PUT UR SALT HERE"

sync = [
	'drive'
]
sync_sleep = 10	# minutes

drive = {
	"client_secrets" : "%sclient_secrets.json" % conf,
	"p12" : "%syour-gdata-privatekey.p12" % conf,
	"asset_root" : "folder_id_on_drive",
	"absorbed_flag" : "absorbedByInformaCam"
}

couch = {
	"login" : "cdb_username:cdb_password",
	"db" : "informa_cam"
}

j3m = {
	"root" : "/where/is/the/j3mifier/",
	"classpath" : "%(j)sframework:%(j)sjars/*:%(j)sconf framework.MediaProcessor" % {'j' : '/where/is/the/j3mifier/'}
}

api = {
	'port' : 6666 	# doesn't have to be!
}

invalidate = {
	'codes' : {
		'source_invalid_pgp_key' : 902,
		'submission_invalid_image' : 900,
		'submission_invalid_video' : 901,
		'access_denied' : 800
	},
	'reasons' : {
		'source_invalid_pgp_key' : "The pgp key at %s is invalid or corrupted",
		'submission_invalid_image' : "The image at %s is invalid or corrupted",
		'submission_invalid_video' : "The video at %s is invalid or corrupted",
		'access_denied' : "The user %s is attempting to access an asset beyond its permissions."
	}
}