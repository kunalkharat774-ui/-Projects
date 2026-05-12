
text = "👋 Hi, I'm Ethical Hacker !"

loop do
  text.each_char do |char|
    print char
    sleep(0.08)
  end

  sleep(0.5)
  print "\r" + (" " * text.length) + "\r"
end