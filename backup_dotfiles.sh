#!/bin/sh

# This script intends to backup my dotfiles to github

DOTFILES_DIR="${HOME}/dev/dotfiles"
DOTFILES_GIT="git@github.com:Pryz/dotfiles.git"

# Usage : copy_to_dig $FILE_TO_BKP $SUBDIR
copy_to_git() {
  if [[ -f $1 ]]; then
    # Create new subdir if needed
    [[ ! -n "$2" ]] && [[ ! -d $2 ]] \
      && mkdir $DOTFILES_DIR/$2
    # Copy file to backup
    cp $1 $DOTFILES_DIR/$2
  else
    echo "File $1 not found. Passing.."
  fi
}

# Ensure the dotfile folder is present
if [[ ! -d $DOTFILES_DIR ]]; then
  mkdir $DOTFILES_DIR
  pushd $DOTFILES_DIR
  git clone $DOTFILE_GIT
  popd
fi

# Backups
copy_to_git "${HOME}/.vimrc" 'vim'
copy_to_git "${HOME}/.i3/config" 'i3'
copy_to_git "${HOME}/.i3/lock.sh" 'i3'
copy_to_git "${HOME}/.i3/status.conf" 'i3'

# Commit to github
pushd $DOTFILES_DIR &>/dev/null

# To detect changes : https://git-scm.com/docs/git-status#_output
[[ -z "$(git status --porcelain | awk '/(??|M)/ {print $2}')" ]] \
  && echo "No change. Exiting..." \
  && exit 0

# Add new files and commit everything
git add .
git commit -am "$(date "+%m-%d-%Y") backups"
git push
