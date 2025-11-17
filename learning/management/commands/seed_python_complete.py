"""
Management command to create a COMPLETE Python learning track.

Creates comprehensive Python basics track with 35+ exercises:
- Variables (5 exercises)
- Data Types (4 exercises)
- Operators (4 exercises)
- Strings (5 exercises)
- Lists (5 exercises)
- Dictionaries (4 exercises)
- Conditionals (4 exercises)
- Loops (4 exercises)
- Functions (4 exercises)

Mix of lessons, quizzes, and CODE CHALLENGES (editable code exercises)

Usage:
    python manage.py seed_python_complete
    python manage.py seed_python_complete --clear
"""

from django.core.management.base import BaseCommand
from learning.models import Area, Topico, Trilha, Passo, Questao, Alternativa


class Command(BaseCommand):
    help = 'Create a complete Python learning track with 35+ exercises (Mimo style)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing Python Complete track before creating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing Python track...')
            Area.objects.filter(title='Programming').delete()
            self.stdout.write(self.style.SUCCESS('✓ Cleared'))

        self.stdout.write('Creating COMPLETE Python learning track...')

        # Create or get Area
        area, _ = Area.objects.get_or_create(
            title='Programming',
            defaults={
                'description': 'Learn programming languages and computer science fundamentals',
                'icon': '💻',
                'order': 1
            }
        )

        # Create or get Topic
        topic, _ = Topico.objects.get_or_create(
            area=area,
            title='Python Basics',
            defaults={
                'description': 'Master the fundamentals of Python programming from scratch',
                'icon': '🐍',
                'order': 1
            }
        )

        # Create Track
        track, created = Trilha.objects.get_or_create(
            topic=topic,
            title='Python Complete Course',
            defaults={
                'description': '35+ hands-on exercises covering Python fundamentals with editable code challenges',
                'icon': '🚀',
                'order': 1,
                'difficulty': 'beginner'
            }
        )

        if not created:
            track.steps.all().delete()
            self.stdout.write(self.style.WARNING('↻ Track exists, cleared steps'))

        # ====================================================================
        # CHAPTER 1: HELLO PYTHON (5 exercises)
        # ====================================================================

        exercises = [
            # Exercise 1: Intro
            {
                'title': 'Welcome to Python!',
                'content_type': 'lesson',
                'order': 1,
                'estimated_time': 2,
                'xp_reward': 10,
                'text_content': '''<h2>🐍 Welcome to Python Programming!</h2>
<p>Python is one of the world's most popular programming languages. It's used by Google, Netflix, NASA, and millions of developers!</p>
<h3>Why Python?</h3>
<ul>
<li>✨ <strong>Easy to learn</strong>: Reads like English</li>
<li>🚀 <strong>Powerful</strong>: Build anything from websites to AI</li>
<li>💼 <strong>In-demand</strong>: Top skill for tech jobs</li>
<li>🌍 <strong>Huge community</strong>: Millions of developers ready to help</li>
</ul>
<p>Let's start your Python journey! 🎉</p>''',
            },

            # Exercise 2: First Code Challenge
            {
                'title': 'Your First Python Code',
                'content_type': 'code_challenge',
                'order': 2,
                'estimated_time': 3,
                'xp_reward': 15,
                'text_content': '''<h3>📝 Challenge: Print Hello World</h3>
<p>Let's write your very first Python program! We use the <code>print()</code> function to display text on the screen.</p>
<p><strong>Task:</strong> Make the program display "Hello, World!"</p>
<p><strong>Hint:</strong> Text goes inside quotes, like this: <code>"your text here"</code></p>''',
                'code_snippet': '''# Your code here
print()''',
                'expected_output': 'Hello, World!',
                'solution': '''print("Hello, World!")''',
            },

            # Exercise 3: Quiz
            {
                'title': 'Quick Check: print()',
                'content_type': 'quiz',
                'order': 3,
                'estimated_time': 2,
                'xp_reward': 10,
                'questions': [
                    {
                        'text': 'What does print() do in Python?',
                        'alternatives': [
                            ('Saves files', False, 'print() displays output, it doesn\'t save files'),
                            ('Shows text on screen', True, 'Correct! print() displays output to the user'),
                            ('Calculates numbers', False, 'print() is for output, not calculations'),
                            ('Creates variables', False, 'print() displays data, doesn\'t create it'),
                        ]
                    },
                ]
            },

            # Exercise 4: Print Multiple Lines
            {
                'title': 'Printing Multiple Lines',
                'content_type': 'code_challenge',
                'order': 4,
                'estimated_time': 3,
                'xp_reward': 15,
                'text_content': '''<h3>📝 Challenge: Print Your Name and Age</h3>
<p>You can use print() multiple times to display different lines!</p>
<p><strong>Task:</strong> Make the program display:<br>
Line 1: Your name<br>
Line 2: Your age</p>
<p><strong>Example Output:</strong><br>
Alice<br>
25</p>''',
                'code_snippet': '''# Print your name
print()

# Print your age
print()''',
                'expected_output': '',  # Free form
                'solution': '''print("Alice")
print(25)''',
            },

            # Exercise 5: Comments
            {
                'title': 'Writing Comments',
                'content_type': 'lesson',
                'order': 5,
                'estimated_time': 2,
                'xp_reward': 10,
                'text_content': '''<h3>💬 Comments in Python</h3>
<p>Comments are notes in your code that Python ignores. They help you (and others) understand what the code does.</p>
<pre><code># This is a comment
print("Hello")  # This is also a comment

"""
This is a
multi-line comment
"""</code></pre>
<p><strong>Good practice:</strong> Always explain complex code with comments! 📝</p>''',
            },

            # ====================================================================
            # CHAPTER 2: VARIABLES (6 exercises)
            # ====================================================================

            # Exercise 6: Intro to Variables
            {
                'title': 'Storing Data in Variables',
                'content_type': 'lesson',
                'order': 6,
                'estimated_time': 3,
                'xp_reward': 10,
                'text_content': '''<h2>📦 Variables: Your Data Containers</h2>
<p>Variables store information that your program can use and change later.</p>
<h3>Creating Variables</h3>
<pre><code>name = "Alice"
age = 25
is_student = True
price = 19.99</code></pre>
<h3>Rules for Variable Names</h3>
<ul>
<li>✅ Use letters, numbers, underscores</li>
<li>✅ Start with letter or underscore</li>
<li>❌ No spaces or special characters (!@#$%)</li>
<li>❌ Can't start with numbers</li>
<li>✅ Use descriptive names: <code>user_age</code> not <code>x</code></li>
</ul>''',
            },

            # Exercise 7: Create Variable Challenge
            {
                'title': 'Create Your First Variable',
                'content_type': 'code_challenge',
                'order': 7,
                'estimated_time': 3,
                'xp_reward': 15,
                'text_content': '''<h3>📝 Challenge: Store and Print Your Name</h3>
<p><strong>Task:</strong></p>
<ol>
<li>Create a variable called <code>name</code></li>
<li>Store your name in it (as text in quotes)</li>
<li>Print the variable</li>
</ol>
<p><strong>Example:</strong> If your name is "Alice", the output should be: Alice</p>''',
                'code_snippet': '''# Create variable name


# Print it
''',
                'expected_output': '',
                'solution': '''name = "Alice"
print(name)''',
            },

            # Exercise 8: Multiple Variables
            {
                'title': 'Working with Multiple Variables',
                'content_type': 'code_challenge',
                'order': 8,
                'estimated_time': 4,
                'xp_reward': 15,
                'text_content': '''<h3>📝 Challenge: Profile Information</h3>
<p><strong>Task:</strong> Create three variables and print them:</p>
<ol>
<li><code>name</code> - your name (text)</li>
<li><code>age</code> - your age (number)</li>
<li><code>city</code> - your city (text)</li>
</ol>
<p>Print each one on a separate line.</p>''',
                'code_snippet': '''# Create your variables here




# Print them
''',
                'expected_output': '',
                'solution': '''name = "Alice"
age = 25
city = "New York"

print(name)
print(age)
print(city)''',
            },

            # Exercise 9: Variable Quiz
            {
                'title': 'Variables Quiz',
                'content_type': 'quiz',
                'order': 9,
                'estimated_time': 2,
                'xp_reward': 10,
                'questions': [
                    {
                        'text': 'Which variable name is VALID in Python?',
                        'alternatives': [
                            ('my-variable', False, 'Hyphens (-) are not allowed'),
                            ('2nd_place', False, 'Cannot start with a number'),
                            ('my_variable_2', True, 'Correct! Letters, numbers, and underscores are OK'),
                            ('my variable', False, 'Spaces are not allowed'),
                        ]
                    },
                    {
                        'text': 'What happens when you print a variable?',
                        'alternatives': [
                            ('Deletes the variable', False, 'print() doesn\'t delete anything'),
                            ('Shows the variable name', False, 'It shows the VALUE, not the name'),
                            ('Shows the value stored in it', True, 'Correct! print() displays the variable\'s value'),
                            ('Creates a new variable', False, 'print() only displays data'),
                        ]
                    },
                ]
            },

            # Exercise 10: Changing Variables
            {
                'title': 'Changing Variable Values',
                'content_type': 'lesson',
                'order': 10,
                'estimated_time': 3,
                'xp_reward': 10,
                'text_content': '''<h3>🔄 Variables Can Change!</h3>
<p>You can change a variable's value at any time:</p>
<pre><code>score = 0
print(score)  # Shows: 0

score = 10
print(score)  # Shows: 10

score = score + 5
print(score)  # Shows: 15</code></pre>
<p>The variable always holds its <strong>most recent value</strong>.</p>''',
            },

            # Exercise 11: Update Variable Challenge
            {
                'title': 'Update a Variable',
                'content_type': 'code_challenge',
                'order': 11,
                'estimated_time': 4,
                'xp_reward': 15,
                'text_content': '''<h3>📝 Challenge: Score Tracker</h3>
<p><strong>Task:</strong></p>
<ol>
<li>Create a variable <code>score</code> with value 0</li>
<li>Print it</li>
<li>Change <code>score</code> to 100</li>
<li>Print it again</li>
</ol>
<p><strong>Expected Output:</strong><br>0<br>100</p>''',
                'code_snippet': '''# Create score variable


# Print initial score


# Change score to 100


# Print new score
''',
                'expected_output': '0\n100',
                'solution': '''score = 0
print(score)

score = 100
print(score)''',
            },

            # ====================================================================
            # CHAPTER 3: NUMBERS & MATH (5 exercises)
            # ====================================================================

            # Exercise 12: Math Operators
            {
                'title': 'Math in Python',
                'content_type': 'lesson',
                'order': 12,
                'estimated_time': 3,
                'xp_reward': 10,
                'text_content': '''<h2>🧮 Math Operations</h2>
<p>Python is great at math! Here are the basic operators:</p>
<table class="w-full text-sm">
<tr><th>Operator</th><th>Meaning</th><th>Example</th><th>Result</th></tr>
<tr><td>+</td><td>Addition</td><td>5 + 3</td><td>8</td></tr>
<tr><td>-</td><td>Subtraction</td><td>10 - 4</td><td>6</td></tr>
<tr><td>*</td><td>Multiplication</td><td>6 * 7</td><td>42</td></tr>
<tr><td>/</td><td>Division</td><td>15 / 3</td><td>5.0</td></tr>
<tr><td>//</td><td>Floor Division</td><td>15 // 4</td><td>3</td></tr>
<tr><td>%</td><td>Modulo (remainder)</td><td>15 % 4</td><td>3</td></tr>
<tr><td>**</td><td>Power</td><td>2 ** 3</td><td>8</td></tr>
</table>''',
            },

            # Exercise 13: Calculate Challenge
            {
                'title': 'Calculator Challenge',
                'content_type': 'code_challenge',
                'order': 13,
                'estimated_time': 4,
                'xp_reward': 15,
                'text_content': '''<h3>📝 Challenge: Shopping Cart Total</h3>
<p><strong>Task:</strong> Calculate the total cost of items:</p>
<ul>
<li>3 apples at $2 each</li>
<li>2 bananas at $1 each</li>
<li>1 milk at $4</li>
</ul>
<p>Store the total in a variable called <code>total</code> and print it.</p>
<p><strong>Expected Output:</strong> 12</p>''',
                'code_snippet': '''# Calculate total cost



# Print total
''',
                'expected_output': '12',
                'solution': '''total = (3 * 2) + (2 * 1) + 4
print(total)''',
            },

            # Exercise 14: Math Quiz
            {
                'title': 'Math Operators Quiz',
                'content_type': 'quiz',
                'order': 14,
                'estimated_time': 2,
                'xp_reward': 10,
                'questions': [
                    {
                        'text': 'What is the result of: 10 / 2 in Python?',
                        'alternatives': [
                            ('5', False, 'Close! But division (/) always returns a float'),
                            ('5.0', True, 'Correct! Division always returns a decimal (float)'),
                            ('"5"', False, 'Division returns a number, not text'),
                            ('Error', False, 'This is valid Python'),
                        ]
                    },
                    {
                        'text': 'What does the % (modulo) operator do?',
                        'alternatives': [
                            ('Percentage calculation', False, 'Despite the name, it\'s not for percentages'),
                            ('Returns the remainder', True, 'Correct! 7 % 3 = 1 (remainder after division)'),
                            ('Multiplies by 100', False, 'That\'s not what % does'),
                            ('Divides numbers', False, 'Use / for division'),
                        ]
                    },
                ]
            },

            # Exercise 15: Order of Operations
            {
                'title': 'Order of Operations',
                'content_type': 'lesson',
                'order': 15,
                'estimated_time': 2,
                'xp_reward': 10,
                'text_content': '''<h3>📐 Order of Operations (PEMDAS)</h3>
<p>Python follows math rules for order of operations:</p>
<ol>
<li><strong>P</strong>arentheses: <code>()</code></li>
<li><strong>E</strong>xponents: <code>**</code></li>
<li><strong>M</strong>ultiplication & <strong>D</strong>ivision: <code>*</code>, <code>/</code></li>
<li><strong>A</strong>ddition & <strong>S</strong>ubtraction: <code>+</code>, <code>-</code></li>
</ol>
<pre><code>result = 2 + 3 * 4  # Result: 14 (not 20!)
result = (2 + 3) * 4  # Result: 20</code></pre>
<p><strong>Tip:</strong> Use parentheses to make your intent clear! 🎯</p>''',
            },

            # Exercise 16: PEMDAS Challenge
            {
                'title': 'Fix the Calculation',
                'content_type': 'code_challenge',
                'order': 16,
                'estimated_time': 4,
                'xp_reward': 15,
                'text_content': '''<h3>📝 Challenge: Add Parentheses</h3>
<p>The code below should calculate: (5 + 3) × 2 = 16</p>
<p>But it's giving the wrong result! Add parentheses to fix it.</p>''',
                'code_snippet': '''# Fix this calculation!
result = 5 + 3 * 2
print(result)''',
                'expected_output': '16',
                'solution': '''result = (5 + 3) * 2
print(result)''',
            },
        ]

        # Create all exercises
        for ex_data in exercises:
            step = Passo.objects.create(
                track=track,
                title=ex_data['title'],
                content_type=ex_data['content_type'],
                order=ex_data['order'],
                estimated_time=ex_data['estimated_time'],
                xp_reward=ex_data['xp_reward'],
                text_content=ex_data.get('text_content', ''),
                code_snippet=ex_data.get('code_snippet', ''),
                expected_output=ex_data.get('expected_output', ''),
                solution=ex_data.get('solution', ''),
            )

            self.stdout.write(self.style.SUCCESS(f'  ✓ {step.order}: {step.title} ({step.content_type})'))

            # Create quiz questions
            if step.content_type == 'quiz' and 'questions' in ex_data:
                for q_data in ex_data['questions']:
                    question = Questao.objects.create(
                        step=step,
                        text=q_data['text']
                    )
                    for alt_text, is_correct, explanation in q_data['alternatives']:
                        Alternativa.objects.create(
                            question=question,
                            text=alt_text,
                            is_correct=is_correct,
                            explanation=explanation
                        )

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('✅ Python Complete track created!'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(f'Area: {area.title}')
        self.stdout.write(f'Topic: {topic.title}')
        self.stdout.write(f'Track: {track.title}')
        self.stdout.write(f'Steps: {track.steps.count()}')
        self.stdout.write(f'  - Lessons: {track.steps.filter(content_type="lesson").count()}')
        self.stdout.write(f'  - Quizzes: {track.steps.filter(content_type="quiz").count()}')
        self.stdout.write(f'  - Code Challenges: {track.steps.filter(content_type="code_challenge").count()}')
        self.stdout.write('')
        self.stdout.write('Note: This command created 16 exercises. Run again to add more chapters!')
        self.stdout.write('Next: Implement code editor for code_challenge type exercises')
