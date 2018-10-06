
Daniel_Kowalski@trendmicro.com
Sun, Sep 30, 1:27 PM (6 days ago)
to me

#!/bin/bash

###############################################################################
#
# iam-user-permissions.sh:
# This script helps to collect policies for IAM user/role and summarize the
# permissions for a subset of permissions stored in permissions.confid file
#
#
# usage: iam-user-permissions.sh -u IAMUSER -a ARN -r REGION
# run this script locally
#
###############################################################################

usage() {
    echo "Usage: $0 -u IAMUSER -a ARN -r REGION"
    exit 1;
}

while getopts ":u:a:r:" o; do
    case "${o}" in
    u)
        IAMUSER=${OPTARG}
        ;;
    a)
        ARN=${OPTARG}
        ;;
    r)
        REGION=${OPTARG}
        ;;
    *)
        ;;
    esac
done

getInputParams() {
  if [ -z $IAMUSER ]; then
     echo "Enter IAM user/role:"
     read IAMUSER
  fi

  if [ -z $REGION ]; then
     echo "Enter region:"
     read REGION
  fi

  if [ -z $ARN ]; then
     echo "Enter ARN:"
     read ARN
  fi
}

processIAM()
{
  #Check if user entered is valid
  aws iam get-user --user-name $IAMUSER  > /dev/null 2>&1
  if [ $? != 0 ]; then
      #Check if value entered is a ROLE
      aws iam get-role --role-name $IAMUSER  > /dev/null 2>&1
      if [ $? != 0 ]; then
         echo "Invalid input: IAM user/role"
         exit 1
      else
         echo "Checking necessary permissions..."
         retrieveRolePermissions
      fi
  else
      echo "Checking necessary permissions..."
      retrieveUserPermissions
  fi
}

retrieveUserPermissions()
{
  #Check if user is part of group
  IAMGROUPS=($(aws iam list-groups-for-user --user-name $IAMUSER --query 'Groups[].GroupName' --output text ))
  for GROUP in "${IAMGROUPS[@]}";
  do
       ATTACHEDPOLICIES=($(aws iam list-attached-group-policies --group-name $GROUP --query 'AttachedPolicies[].PolicyArn' --output text ))
       for APOLICY in "${ATTACHEDPOLICIES[@]}"
       do
           parseAttachedPolicies $APOLICY
       done

       INLINEPOLICIES=($(aws iam list-group-policies --group-name $GROUP --query 'PolicyNames' --output text ))

       for IPOLICY in "${INLINEPOLICIES[@]}"
       do
           IPOLICYRULES=$(aws iam get-group-policy --group-name $GROUP --policy-name $IPOLICY --query 'PolicyDocument.Statement[]' )
           parsePolicyRules "$IPOLICYRULES"
       done
  done

  #Check attached user policies
  ATTACHEDPOLICIES=($(aws iam list-attached-user-policies --user-name $IAMUSER --query 'AttachedPolicies[].PolicyArn' --output text ))
  
  for APOLICY in "${ATTACHEDPOLICIES[@]}"
  do
      parseAttachedPolicies $APOLICY
  done

  INLINEPOLICIES=($(aws iam list-user-policies --user-name $IAMUSER --query 'PolicyNames' --output text ))

  for IPOLICY in "${INLINEPOLICIES[@]}"
  do
      IPOLICYRULES=$(aws iam get-user-policy --user-name $IAMUSER --policy-name $IPOLICY --query 'PolicyDocument.Statement[]' )
      parsePolicyRules "$IPOLICYRULES"
  done
}


retrieveRolePermissions()
{
  #Check attached role policies
  ATTACHEDPOLICIES=($(aws iam list-attached-role-policies --role-name $IAMUSER --query 'AttachedPolicies[].PolicyArn' --output text ))
  for APOLICY in "${ATTACHEDPOLICIES[@]}"
  do
      parseAttachedPolicies $APOLICY
  done
 

  INLINEPOLICIES=($(aws iam list-role-policies --role-name $IAMUSER --query 'PolicyNames' --output text ))
  for IPOLICY in "${INLINEPOLICIES[@]}"
  do
      IPOLICYRULES=$(aws iam get-role-policy --role-name $IAMUSER --policy-name $IPOLICY --query 'PolicyDocument.Statement[]' )
      parsePolicyRules "$IPOLICYRULES"
  done
}


parseAttachedPolicies()
{
  POLICYARN=$1
  POLICYVERSION=$(aws iam get-policy --policy-arn $POLICYARN --query 'Policy.DefaultVersionId' --output text )

  #Get policy and collect all policy rules
  APOLICYRULES="$(aws iam get-policy-version --policy-arn $POLICYARN --version-id $POLICYVERSION --query 'PolicyVersion.Document.Statement[]' )"
  parsePolicyRules "$APOLICYRULES"
}


parsePolicyRules()
{
  POLICYCONTENT="$1"
  readarray -t POLICIES <<< "$(parsePolicyJson $POLICYCONTENT)"
  for POLICY in "${POLICIES[@]}"
  do
     ACTIONS=($(echo $POLICY))
     EFFECT=${ACTIONS[-1]}
     unset 'ACTIONS[${#ACTIONS[@]}-1]'
     APPLYEFFECT=$([ $EFFECT == 'Allow' ] && echo "PASS" || echo "FAIL")
     CURRENTEFFECT=$([ $EFFECT == 'Allow' ] && echo "FAIL" || echo "PASS")
     
     if [ -z $ACTIONS ];
     then
        #We grant EFFECT to all permissions
        PERMISSIONARRAY=("${PERMISSIONARRAY[@]/%$CURRENTEFFECT/$APPLYEFFECT}")
     fi

     for ACTION in "${ACTIONS[@]}"
     do
        for PERMISSION in "${!PERMISSIONARRAY[@]}"
        do
           if [[ -z ${PERMISSIONARRAY[$PERMISSION]##$ACTION*} ]];
           then
                PERMISSIONARRAY[$PERMISSION]="${PERMISSIONARRAY[$PERMISSION]/%$CURRENTEFFECT/$APPLYEFFECT}"
           fi
        done
      done
   done
}


parsePolicyJson () {
    python <<EOF
import json
data_action=[]
data_effect=[]
parsed_policy = json.loads('''${@}''')

for index, policy in enumerate(parsed_policy):
    for child in policy['Action']:
      print child.replace("*",""),

    print policy['Effect']
    if 'Condition' in policy:
      print (index,policy['Condition'])
EOF
}


#Read all required permissions from config file placed in current directory
CURRENTDIR=`dirname $(readlink -f "$0")`
declare -a PERMISSIONARRAY="($(<$CURRENTDIR/permissions.config))"

#Append each permission value with FAIL as initially IAM user/role have no permissions
PERMISSIONARRAY=("${PERMISSIONARRAY[@]/%/ FAIL}")

#If input parameter are not provided on command line then we prompt user to enter the same
getInputParams

#Start processing all provided inputs
processIAM

#foo="$(cat $CURRENTDIR/policy4.json)"

#parsePolicyRules "$foo"

printf '%s\n' "${PERMISSIONARRAY[@]}"
