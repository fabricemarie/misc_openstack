#!/usr/bin/env python
"""
Create multiple similar cinder volumes one after the other.
Author Fabrice A. Marie
Date 2015-02-12
Copyright (C) 2015 Kibin Labs Pte Ltd. Released under MIT license.
"""

import sys
import logging
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s')
l = logging.getLogger(__name__)
l.setLevel(logging.INFO)
try:
    import argparse
except Exception as exc:
    l.error("python-argparse is not installed. Install it and try again. "
            "Exception was: {0}".format(exc))
    sys.exit(1)
try:
    from cinderclient import client
except Exception as exc:
    l.error("python-cinderclient is not installed. Install it and try again. "
            "Exception was: {0}".format(exc))
    sys.exit(1)
import time
import os

username = None
username_required = True
if "OS_USERNAME" in os.environ.keys():
    username = os.environ["OS_USERNAME"]
    username_required = False
password = None
password_required = True
if "OS_PASSWORD" in os.environ.keys():
    password = os.environ["OS_PASSWORD"]
    password_required = False
tenant = None
tenant_required = True
if "OS_TENANT_NAME" in os.environ.keys():
    tenant = os.environ["OS_TENANT_NAME"]
    tenant_required = False
auth_url = None
auth_url_required = True
if "OS_AUTH_URL" in os.environ.keys():
    auth_url = os.environ["OS_AUTH_URL"]
    auth_url_required = False

version = "1.0"
description = "Create multiple similar cinder volumes one after the other."
epilog = "Copyright (c) 2015 Kibin Labs Pte Ltd. Released under MIT license."
parser = argparse.ArgumentParser(description=description, epilog=epilog)
parser.add_argument('--os-username', help="The OpenStack user's username to "
                    "use to connect to OpenStack Keystone",
                    required=username_required, metavar='username',
                    default=username)

parser.add_argument('--os-password', help="The OpenStack user's password to "
                    "use to connect to OpenStack Keystone",
                    required=password_required, metavar='password',
                    default=password)

parser.add_argument('--os-tenant-name', help="The OpenStack user's tenant "
                    "name to use to connect to OpenStack Keystone",
                    required=tenant_required, metavar='tenant_name',
                    default=tenant)

parser.add_argument('--os-auth-url', help="The OpenStack Keystone "
                    "authentication URL",
                    required=auth_url_required, metavar='auth_URL',
                    default=auth_url)

parser.add_argument('--name', help="The volume name template to use, "
                    "after which we will add a dash and an index number. "
                    "Defaults to 'volume'",
                    required=False, metavar='template', default="volume")

parser.add_argument('--size', help="The size in GB of each volume to create",
                    required=True, metavar='GB_size', type=int)

parser.add_argument('--volume-type', help="The cinder volume-type name to use "
                    "for volume creation",
                    required=True, metavar='voltype_name')

parser.add_argument('--poll-frequency', help="The frequency in seconds at "
                    "which to poll cinder for completion. Defaults to 30.",
                    required=False, metavar='seconds', type=int, default=30)

parser.add_argument('--number-volumes', help="The number of cinder volumes to "
                    "create", required=True, metavar='number', type=int)

parser.add_argument('--start-index', help="The index to start with for volume"
                    " creation, this index is incremented at each volume "
                    "created. Defaults to 1.", required=False, metavar='index',
                    type=int, default=1)

parser.add_argument('--image-id', help="Create volume from image id. Defaults "
                    "to None", required=False, metavar='ID', default=None)

parser.add_argument('--snapshot-id', help="Create volume from snapshot id. "
                    "Default None", required=False, metavar='ID', default=None)

parser.add_argument('--source-volid', help="Create volume from volume id. "
                    "Defaults to None.", required=False, metavar='ID',
                    default=None)

parser.add_argument('--availability-zone', help="Availability zone for volume."
                    " Defaults to None.",
                    required=False, metavar='zone', default=None)

parser.add_argument('--version', action='version', version=version)

args = parser.parse_args()

# connect to keystone
try:
    c = client.Client('1', args.os_username, args.os_password,
                      args.os_tenant_name, args.os_auth_url)
except Exception as exc:
    l.error("Exception while trying to log on to keystone to get a cinder "
            "endpoint. Exception was: {0}".format(exc))
    sys.exit(1)

# find out the volume type ID we need
voltype_id = None
try:
    for voltype in c.volume_types.list():
        if voltype.name == args.volume_type:
            voltype_id = voltype.id
    if voltype_id is None:
        l.error("Could not find volume_type name {0}".format(args.volume_type))
        sys.exit(1)
except Exception as exc:
    l.error("Exception while looking up volume_type named {0}. Exception was: "
            "{1}".format(args.volume_type, exc))
    sys.exit(1)

for volume_index in range(args.start_index,
                          args.start_index + args.number_volumes):
    # create the volume
    volume_name = "{0}-{1}".format(args.name, volume_index)
    additional_params = {}
    if not args.image_id is None:
        additional_params["imageRef"] = args.image_id
    if not args.snapshot_id is None:
        additional_params["snapshot_id"] = args.snapshot_id
    if not args.source_volid is None:
        additional_params["source_volid"] = args.source_volid
    if not args.availability_zone is None:
        additional_params["availability_zone"] = args.availability_zone
    try:
        vol = c.volumes.create(display_name=volume_name, size=args.size,
                               volume_type=voltype_id, **additional_params)
        l.info("Initiated creation of volume {0} with volume-id "
               "{1}".format(volume_name, vol.id))
    except Exception as exc:
        l.error("Exception while creating volume {0}. Exception was: "
                "{1}".format(volume_name, exc))
        continue

    volume_is_ready = False
    volume_is_error = True
    while True:
        # check that the volume is in the correct State
        try:
            current_vol = c.volumes.get(vol.id)
        except Exception as exc:
            l.error("Could not check status of volume {0} with ID "
                    "{1}".format(volume_name, vol.id))
            break
        # volume is no longer creating? then it's done or error
        if current_vol.status != "creating":
            volume_is_ready = True
            if current_vol.status == "available":
                volume_is_error = False
            break
        # sleep and check again later
        l.info("Waiting for volume {0}. Current state is '{1}'. Sleeping "
               "{2} seconds.".format(volume_name, current_vol.status,
                                     args.poll_frequency))
        time.sleep(args.poll_frequency)

    if not volume_is_ready:
        continue

    if volume_is_error:
        l.error("Error creating volume {0}".format(volume_name))
        continue

    l.info("Successfully created volume {0}".format(volume_name))
