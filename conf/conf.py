conf = "/where/you/put/your/conf/"
assets_root = "/where/you/put/your/submitted/assets/"
submissions_dump = "%ssubmissions/" % assets_root
gnupg_home = '/where/you/want/gpg/to/be/'
forms_root = "/where/you/put/your/javarosa/forms/"

scripts_home = {
	"python" : '/where/you/put/your/scripts/py/'
}

file_salt = "YOU PUT UR SALT HERE"

sync = [
	'drive', 'globaleaks'
]
sync_sleep = 10	# minutes
validity_buffer = {
	'location' : (5 * 60 * 1000), # 5 minutes
	'stale_data' : ((((60 * 1000) * 60) * 24) * 30) # 30 days
}

wigle = {
	'username' : 'username',
	'password' : 'password',
	'base_url' : "https://wigle.net/",
	'login_url' : "gps/gps/main/login",
	'logout_url' : "gps/gps/main/logout",
	'cookie_jar' : "%swigle_cookiejar.txt" % conf,
	'query_url' : "gps/gps/main/confirmlocquery/",
	'query' : {
		'bssid' : "netid",
		'ssid' : "ssid",
		'lat_south' : 'latrange1',
		'lat_north' : 'latrange2',
		'lon_east' : 'longrange1',
		'lon_west' : 'longrange2'
	}
}

drive = {
	"client_secrets" : "%sclient_secrets.json" % conf,
	"p12" : "%syour-gdata-privatekey.p12" % conf,
	"asset_root" : "folder_id_on_drive",
	"absorbed_flag" : "absorbedByInformaCam"
}

globaleaks = {
	"asset_root" : "/where/globaleaks/is/files/submission/",
	"host" : "host url",
	"user" : "user (ubuntu?)",
	"identity_file" : "%sid_file_to_gl_server.pem" % conf,
	"absorbed_log" : "absorbedByInformaCam_gl.json",
	"absorbed_flag" : "absorbedByInformaCam",
	"public_url" : "http://maybe_a.onion?"
}

organization_fingerprint = "PGP KEY FINGERPRING"
organization_name = "WHO ARE YOU?"
organization_details = "A blurb"
public_key_path = '/where/is/your/public/key.asc'

repositories = [
	{
		'source': 'google_drive',
		'asset_root': drive['asset_root']
	},
	{
		'source': 'globaleaks',
		'asset_root': globaleaks['public_url']
	}

]

forms = [
	'%sa_form_you_made.xml' % forms_root,
	'%sanother_form_you_made.xml' % forms_root
]

couch = {
	"login" : "cdb_username:cdb_password",
	"db" : "informa_cam"
}

j3m = {
	"root" : "/where/is/the/j3mifier/",
	"classpath" : ".:%(j)sframework:%(j)sjars/*:%(j)sconf" % {'j' : '/where/is/the/j3mifier/'}
}

api = {
	'port' : 6666 	# doesn't have to be!
}

invalidate = {
	'codes' : {
		'asset_non_existent': 801,
		'source_invalid_pgp_key' : 902,
		'source_invalid_public_credentials' : 903,
		'source_missing_pgp_key' : 905,
		'submission_invalid_image' : 900,
		'submission_invalid_video' : 901,
		'submission_invalid_j3m' : 904,
		'access_denied' : 800
	},
	'reasons' : {
		'asset_non_existent': "The requested asset does not exist",
		'source_invalid_pgp_key' : "The pgp key at %s is invalid or corrupted",
		'source_missing_pgp_key' : "This source has no PGP key in the keyring",
		'source_invalid_public_credentials' : "One or more of the public credentials files are invalid or corrupted",
		'submission_invalid_image' : "The image at %s is invalid or corrupted",
		'submission_invalid_video' : "The video at %s is invalid or corrupted",
		'submission_invalid_j3m' : "The j3m for this submission is invalid or missing",
		'access_denied' : "The user %s is attempting to access an asset beyond its permissions."
	}
}

public = {
	"organizationName" : organization_name,
	"organizationDetails" : organization_details,
	"organizationFingerprint" : organization_fingerprint,
	"repositories": repositories,
	"publicKey": public_key_path,
	"forms": forms
}

context_codes = {
	'reportedBy': {
		'source' : 700,
		'wigle' : 701
	}
}
