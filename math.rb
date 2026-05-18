# ======================================
# Ruby Maths Quiz Game
# Random Font Colour Version
# ======================================

# ANSI colour codes
COLORS = [
  31, # Red
  32, # Green
  33, # Yellow
  34, # Blue
  35, # Magenta
  36, # Cyan
  91, # Bright Red
  92, # Bright Green
  93, # Bright Yellow
  94, # Bright Blue
  95, # Bright Magenta
  96  # Bright Cyan
]

# Method for colourful text
def colour_text(text)
  colour = COLORS.sample
  "\e[#{colour}m#{text}\e[0m"
end

score = 0
rounds = 10

puts colour_text("===================================")
puts colour_text("      RUBY MATHS QUIZ GAME")
puts colour_text("===================================")
puts

rounds.times do |i|
  num1 = rand(1..20)
  num2 = rand(1..20)

  operations = ["+", "-", "*"]
  op = operations.sample

  correct_answer = case op
                   when "+"
                     num1 + num2
                   when "-"
                     num1 - num2
                   when "*"
                     num1 * num2
                   end

  puts colour_text("Question #{i + 1}:")
  print colour_text("What is #{num1} #{op} #{num2}? ")

  user_answer = gets.to_i

  if user_answer == correct_answer
    puts colour_text("✅ Correct!")
    score += 1
  else
    puts colour_text("❌ Wrong!")
    puts colour_text("Correct Answer: #{correct_answer}")
  end

  puts colour_text("Current Score: #{score}")
  puts colour_text("-----------------------------")
end

puts
puts colour_text("===================================")
puts colour_text("Game Over!")
puts colour_text("Final Score: #{score} / #{rounds}")
puts colour_text("===================================")

if score == rounds
  puts colour_text("🏆 Perfect Score!")
elsif score >= 7
  puts colour_text("🔥 Great Job!")
elsif score >= 4
  puts colour_text("👍 Nice Try!")
else
  puts colour_text("💡 Practice More!")
end
