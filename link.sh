#!/bin/bash
echo "Setting up environment..."
apt update
apt install -y zsh
conda init zsh

# Clone dotfiles repository
cd ~
git clone https://github.com/nickypro/.arena_dotfiles.git

# Install Oh My Zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Install Zsh plugins
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k"
git clone https://github.com/zsh-users/zsh-autosuggestions.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
git clone https://github.com/zsh-users/zsh-history-substring-search ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-history-substring-search
git clone https://github.com/zsh-users/zsh-completions ${ZSH_CUSTOM:-${ZSH:-~/.oh-my-zsh}/custom}/plugins/zsh-completions
  
# Create symbolic links
ln -s ~/.arena_dotfiles/.zshrc ~/.zshrc
ln -s ~/.arena_dotfiles/.vimrc ~/.vimrc
ln -s ~/.arena_dotfiles/.p10k.zsh ~/.p10k.zsh

# Reload Zsh to apply changes
source ~/.zshrc
