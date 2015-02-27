#Example of how we create a user in the eMagz app
def create_user(request):
    try:
        new_username = request.POST['new_user']
        new_password = request.POST['new_pw']
        new_email = request.POST['new_email']
    except (KeyError):
        return render(request, 'ebook/demowiz2_reg.html', {
            'error_message':"Compulsory field(s) are missing",
        })

    if(User.objects.filter(username=new_username).exists()):
        return render(request, 'ebook/demowiz2_reg.html', {
            'error_message':"User " + new_username + " already exists",
        })
    else:
        user = User.objects.create_user(new_username, password=new_password)
        user.email = new_email
        user.save()
        
        result = get_reg_url(user.username, user.email)
        #Render page with the registration URL
        if result:
            return render(request, 'ebook/demowiz_final.html', {
                    'regis_url': result
                })
        else:
            return render(request, 'ebook/demowiz2_reg.html', {
                    'error_message': "No result returned from agentcore.get_reg_url()"
                })


#Function to get the registration URL
#Please use this function as it is. No changes required to this function
def get_reg_url(uid_sp, id_email):
    
    if not uid_sp:
        raise ValueError('uid_sp is required!')
    if not id_email:
        raise ValueError('id_email is required!')

    #First get the token for the user to access the registration page
    protocol = 'http'
    auth_server_ip = '128.199.218.44'
    api_getregtoken = '/api/v1/srv/getregtoken/'
    
    gettoken_url = protocol + '://' + auth_server_ip + api_getregtoken
    post_data = {'id_sp' : '123456',
        'uid_sp' : uid_sp,
        'id_email' : id_email}
    
    request = urllib2.Request(gettoken_url, urllib.urlencode(post_data))
    post_resp = urllib2.urlopen(request)
    
    tok_resp = json.loads(post_resp.read())
    if tok_resp['failure'].upper() != 'NO':
        #log.error("Auth Server Error: " + tok_resp['result'])
        return None

    #No errors, so we can build the URL with the token and return it
    api_reg_handler = '/api/v1/srv/getregpage/'
    regfront_url = protocol + '://' + auth_server_ip + api_reg_handler
    reg_data = {'token' : tok_resp['result'] }
    regpage_url = regfront_url + '?' + urllib.urlencode(reg_data)
    
    return regpage_url