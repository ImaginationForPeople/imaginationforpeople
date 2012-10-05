# Require any additional compass plugins here.

require 'fileutils'

require 'bundler/setup'
require 'compass_twitter_bootstrap'

# Set this to the root of your project when deployed:
http_path = "/"
css_dir = "compiled_sass"
sass_dir = "sass"
images_dir = "images"
javascripts_dir = "js"
fonts_dir = "fonts"

generated_images_dir = "compiled_images"
sprite_load_path = "sprites"

# You can select your preferred output style here (can be overridden via the command line):
# :expanded or :nested or :compact or :compressed
output_style = :expanded 

# To enable relative paths to assets via compass helper functions. Uncomment:
relative_assets = true

# To disable debugging comments that display the original location of your selectors. Uncomment:
line_comments = false


# If you prefer the indented syntax, you might want to regenerate this
# project again passing --syntax sass, or you can uncomment this:
# preferred_syntax = :sass
# and then run:
# sass-convert -R --from scss --to sass sass scss && rm -rf sass && mv scss sass
#

sass_options = {:unix_newlines=>true}
line_comments = false
preferred_syntax = :scss
 
# Rename sprites to remove the Compass-generated hash
on_sprite_saved do |filename|
	newname = filename.gsub(%r{-s[a-z0-9]{10}\.png$}, '.png')
	if File.exists?(filename)
		FileUtils.mv filename, newname
	end
	puts "\t  => Renamed to #{File.basename newname}"
	newname
end

# Replace in stylesheets generated references to sprites
# by their counterparts without the hash uniqueness.
on_stylesheet_saved do |filename|
  if File.exists?(filename)
	fnew = File.open(filename + ".new", 'w+')
	fold = File.open(filename, 'r')
	fold.readlines.each do |li|
		case li
		when /([0-9.]+)rem(\s*)/ then
			# compute and rewrite for IE8
			val_px = ($1.to_f * 10).to_i
			fnew << li.gsub(/([0-9.]+)rem(\s*)/, '%spx\2' % val_px)
			# real rule
			fnew << li
		when /-s[a-z0-9]{10}\.png/ then
			fnew << li.gsub(%r{-s[a-z0-9]{10}\.png}, '.png')
		else
			# simple copy
			fnew << li
		end
	end
	FileUtils.mv filename + ".new", filename
    #css = File.read filename
	
    #File.open(filename, 'w+') do |f|
    #  f << css.gsub(%r{-s[a-z0-9]{10}\.png}, '.png')
    #end
  end
end


