from password_strength import PasswordPolicy

def pw_strong_enough(password: str) ->bool:

    policy = PasswordPolicy.from_names(
        length=10,  # min length: 8
        uppercase=1,  # need min. 2 uppercase letters
        numbers=1,  # need min. 2 digits
        nonletters=1,  # need min. 2 non-letter characters
    )

    password = 'AB12#xyZ'
    print(policy.test(password))
    return len(policy.test(password)) == 0
    
print (pw_strong_enough('AB12#xyvfdvndiof3rifq3f345080oZ'))
