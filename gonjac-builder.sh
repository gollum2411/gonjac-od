#!/bin/bash

repos_dir=~/repos

function abort {
    echo $1 >&2
    echo "Aborting!"
    exit 1
}

function usage {
    echo "Usage: gonjac_builder.sh -r <repo> -b <branch> -i <identifier> [-f <flags>]">&2
}

while getopts "r:b:f:i:" opt ; do
    case $opt in
    r)
        repo_name=$OPTARG
        ;;
    b)
        branch=$OPTARG
        ;;
    f)
        flags=$OPTARG
        ;;
    i)
        ID=$OPTARG
        ;;
    \?)
        usage
        exit 1
    esac
done

if [ -z $repo_name ]; then
    usage
    abort "Repo was not specified"
    exit 1
fi

if [ -z $branch ]; then
    usage
    abort "Branch was not specified"
    exit 1
fi

if [ -z $ID ]; then
    usage
    abort "ID was not specified"
    exit 1
fi

gonjac_dir="/tmp/gonjac-od"
repo_dir="$repos_dir/$repo_name"
repo_out="$gonjac_dir/$repo_name-$branch-$ID"
tar_name="$repo_name-$branch-$ID"

pushd $repo_dir || abort "No such repo"
git pull
git checkout $branch || abort "Branch does not exist"
make clean
make -j || abort "Compilation failed"
popd

cp -r $repo_dir $repo_out
pushd $gonjac_dir
pushd $tar_name
echo "Removing .git directory from $(pwd)"
rm -rf $repo_out/.git
popd #$tar_name
tar -zcvf $tar_name.tar.gz $tar_name
rm -rf $tar_name
popd
