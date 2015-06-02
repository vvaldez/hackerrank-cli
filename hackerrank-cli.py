# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

# Import modules
try:
    import xmlrpclib, os, sys, signal, time, re, getpass, urllib, urllib2, requests, json, logging, csv, json, tempfile, io, ConfigParser
    from optparse import OptionParser
    from urllib2 import Request, urlopen, URLError
except:
    print "Could not import modules"
    raise

# config parsing
config = ConfigParser.RawConfigParser()
config.read('.hackerrank-cli')
api_key = config.get('Defaults', 'api_key')
test_id = config.get('Defaults', 'test_id')

tests_url = 'https://www.hackerrank.com/x/api/v2/tests'
tests_url_params = {
	'limit': '-1', 
	'access_token': api_key
	}
question_url = 'https://www.hackerrank.com/x/api/v1/questions/'
question_url_params = {
	'access_token': api_key
	}

url_headers = {'content-type': 'application/json'}

scripts = ['setup','check','solve','cleanup']

# options parsing
usage = "\n%prog [options]\n\nThis script will get and put tests questions and scripts via the HackerRank API."
description = "Use -h or --help for all available options."
parser = OptionParser(usage=usage, description=description)
#parser.add_option("-i", "--interactive", action="store_true", dest="interactive", help="Interactive Mode", default=False)
parser.add_option("-g", "--get", action="store_true", dest="get", help="Get data", default=False)
parser.add_option("-p", "--put", action="store_true", dest="put", help="Put data", default=False)
parser.add_option("-T", "--tests", action="store_true", dest="tests", help="All Tests", default=False)
parser.add_option("-Q", "--questions", action="store_true", dest="questions", help="All Questions", default=False)
parser.add_option("-t", "--test", dest="test_id", help="Test ID", default=test_id)
parser.add_option("-q", "--question", dest="question_id", help="Question ID")
parser.add_option("-k", "--api-key", dest="api_key", help="API Key", default=api_key)
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", help="Enable verbose output", default=False)
parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False, help="Enable lots of debug output (more than verbose)")

(options, terms) = parser.parse_args()

# Perform some setup tasks
if options.verbose:
    print "INFO: Using API KEY: %s" % options.api_key
    print "INFO: Using Test ID: %s" % options.test_id
error = False
if not (options.tests or options.test_id or options.questions):
    print "ERROR: All of what? Specify tests or questions."
    error = True
if not (options.tests or options.test_id):
    print "ERROR: What test?"
if not (options.get or options.put):
    print "ERROR: You have to put or get!"
    error = True
if options.get and options.put:
    print "ERROR: You can't put and get at the same time!"
    error = True
if error:
    print description
    sys.exit(1)

def get_data(url, parameters):
    r = requests.get(url, params=parameters)
    return r.json()

def put_data(url, params, payload):
    r = requests.post(url, headers=url_headers, params=params, data=json.dumps(payload))
    return r

def get_tests(url, params):
    return get_data(url, params)

def get_questions(test_id):
    tests = get_tests(tests_url, tests_url_params)['data']
    for test in tests:
        if options.verbose:
            print "checking test id: %s for matching %s with %s" % (test['id'], test_id, test['questions_array'])
        if str(test['id']) == str(test_id):
            if options.verbose:
                print "INFO: Found match at %s retrieving question array: %s" % (test['id'], test['questions_array'])
            return test['questions_array']

def get_question(q_id):
    return get_data(question_url + q_id, question_url_params)

def put_question(url, params, payload):
    return put_data(url, params, payload)

def write_q_to_disk(test_name, test_id, q_name, q_id, script_name, script):
    if options.verbose: 
        print "INFO: Writing %s, %s, %s" % (test_name, q_name, script_name)
    try:
        os.makedirs("%s/%s" % (test_name, q_name))
    except OSError:
        pass
    if options.debug:
        print "DEBUG: script contents as passed to function: %s" % script
    if script_name == "question_id":
        with open('%s/%s/question_id.txt' % (test_name, q_name), 'w') as outfile:
            outfile.write(q_id)
    elif script_name == "test_id":
        with open('%s/test_id.txt' % test_name, 'w') as outfile:
            outfile.write(str(test_id))
    else:
        with open('%s/%s/%s' % (test_name, q_name, script_name), 'w') as outfile:
            outfile.write(script)

def read_q_from_disk(test_name, q_name, script_name):
    if options.verbose: print "INFO: Reading %s, %s, %s" % (test_name, q_name, script_name)
    with open('%s/%s/%s' % (test_name, q_name, script_name), 'r') as infile:
        script = infile.read()
    if options.debug:
        print "DEBUG: script contents as read from disk: %s" % script
    return script

def main(args):
    if options.get:
        if options.verbose: 
            print "INFO: Get requested"
        # Retrieve all tests
        if options.tests:
                if options.verbose: 
                        print "INFO: All tests requested."
                tests = get_tests(tests_url, tests_url_params)['data']
                print "--------+------------------------------------"
                print "| Test ID | Name "
                print "--------+------------------------------------"
                for test in tests:
                        print "%s   | %s" % (test['id'], test['name'])
                print "--------+------------------------------------"
        # To retrieve all questions for a specific test
        elif options.test_id:
            if options.verbose: 
                print "test %s" % test_id
                print "options %s " % options.test_id
                print "INFO: Test %s requested." % options.test_id
            questions = get_questions(options.test_id)
            print "Questions: "
            print "--------------+------------------------------------"
            print "| Question ID | Name "
            print "--------------+------------------------------------"
            for question in questions:
                    print "%s | %s " % (question, options.test_id)
            print "--------------+------------------------------------"
            # Get test data to retrieve test name
            tests = get_tests(tests_url, tests_url_params)['data']
            for test in tests:
                    if str(test['id']) == str(options.test_id):
                            test_name = test['name']
            # To retrieve all scripts for a question
            if options.questions:
                for question_id in questions:
                    if options.verbose:
                            print "Retrieving scripts for: %s" % question_id
                    question = get_question(question_id)['model']
                    q_name = question['name']
                    for script in scripts:
                            write_q_to_disk(test_name, options.test_id, q_name, question_id, script, question['sudorank_scripts'][script])
                    write_q_to_disk(test_name, options.test_id, q_name, question_id, "test_id", str(options.test_id))
                    write_q_to_disk(test_name, options.test_id, q_name, question_id, "question_id", question_id)
            elif options.question:
                if options.verbose: 
                        print "INFO: Question %s requested." % question_id
                questions = get_questions(options.test_id)
                write_q_to_disk(test_name, options.test_id, q_name, question_id, script, question['sudorank_scripts'][script])
                write_q_to_disk(test_name, options.test_id, q_name, question_id, "test_id", str(options.test_id))
                write_q_to_disk(test_name, options.test_id, q_name, question_id, "question_id", question_id)
        # To retrieve a single question
        elif options.question and options.test_id:
                if options.verbose: 
                        print "INFO: Test %s Question %s requested." % (options.test_id, options.question)
                questions = get_questions(options.test_id)
    elif options.put:
        if options.verbose: 
            print "INFO: Put requested"
        questions = get_questions(options.test_id)
        print "Questions: ",
        for question in questions:
                print "%s " % question,
        print
        tests = get_tests(tests_url, tests_url_params)['data']
        for test in tests:
            if str(test['id']) == str(options.test_id):
                test_name = test['name']
        # To load all scripts for a question
        for question_id in questions:
            print "Reading scripts from disk for: %s" % question_id
            question = get_question(question_id)['model']
            q_name = question['name']
            for script in scripts:
                    question['sudorank_scripts'][script] = read_q_from_disk(test_name, q_name, script)
            request = put_question(question_url + question_id, question_url_params, question)
            print "Put question %s %s %s:" % (q_name, request.status_code, request.headers)
        if options.verbose: 
            print json.dumps(question, sort_keys=True, indent=4, separators=(',', ': '))
		
if __name__ == '__main__':
	main(sys.argv)
