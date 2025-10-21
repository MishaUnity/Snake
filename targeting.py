import numpy

testBuffer = []

buffer = []

DEFAULT_DIRECTION = 'Down'

def get_move_from_buffer():
    if len(buffer) == 0:
        return DEFAULT_DIRECTION

    direction = buffer[0]['dir']

    global testBuffer
    testBuffer = buffer[0]['body']

    buffer.pop(0)
    return direction

def start_search(snake_body, head_pos, fruit_pos, cell_size, width, height):
    body_array = generate_body(snake_body, cell_size)
    map_array = generate_array(body_array, cell_size, width, height)

    history = []
    tested = []
    pos = [int(head_pos[0] / cell_size), int(head_pos[1] / cell_size)]
    target = [int(fruit_pos[0] / cell_size), int(fruit_pos[1] / cell_size)]

    done = False

    global testBuffer
    #testBuffer = body_array.copy()

    for i in range(90000):
        if done:
            return

        min = None
        for step in search_step(map_array, pos, target):
            if not step == None:
                if min == None or min['weight'] > step['weight']:
                    flag = True
                    for tested_cell in tested:
                        if tested_cell == step['index']:
                            flag = False
                            break
                    if flag:
                        min = step
        if not min == None:
            if len(history) > 0:
                history[len(history) - 1]['tested'].append(min['index'])

            #testBuffer = body_array

            direction = 'RIGHT'
            if min['index'] == 1: direction = 'LEFT'
            if min['index'] == 2: direction = 'DOWN'
            if min['index'] == 3: direction = 'UP'

            step_data = {'body': body_array.copy(), 'pos': min['pos'].copy(), 'tested': tested.copy(), 'dir': direction}
            history.append(step_data)
            tested.clear()

            body_array.insert(0, pos)
            body_array.pop(len(body_array) - 1)
            map_array = generate_array(body_array, cell_size, width, height)

            pos = min['pos']

            if pos == target:
                print("Маршрут найден! Длина маршрута:", len(history))
                print("Итерации: ", i)
                global buffer
                buffer = history
                done = True
        else:
            if len(history) > 1:
                history.pop(len(history) - 1)

            index = len(history) - 1
            body_array = history[index]['body'].copy()
            map_array = generate_array(body_array, cell_size, width, height)
            pos = history[index]['pos']
            tested = history[index]['tested'].copy()

    print("Маршрут не найден, превышен лимит итераций")

def search_step(map, pos, target):
    variants = []

    variants.append(calculate_weight(map, [pos[0] + 1, pos[1]], target, 0))
    variants.append(calculate_weight(map, [pos[0] - 1, pos[1]], target, 1))
    variants.append(calculate_weight(map, [pos[0], pos[1] + 1], target, 2))
    variants.append(calculate_weight(map, [pos[0], pos[1] - 1], target, 3))

    return variants

def calculate_weight(map, pos, target, index):
    if len(map) <= pos[0] or len(map[0]) <= pos[1] or pos[0] < 0 or pos[1] < 0:
        return None

    if map[pos[0], pos[1]] == -1:
        return None
    
    distance = numpy.sqrt((pos[0] - target[0])**2 + (pos[1] - target[1])**2)

    barrier_count = 0
    for x in range(pos[0] - 4, pos[0] + 4):
        for y in range(pos[1] - 4, pos[1] + 4):
            if not (len(map) <= x or len(map[0]) <= y or x < 0 or y < 0):
                barrier_count = barrier_count - map[x, y] * min(distance / 5, 1)

    #weight = distance + barrier_count
    weight = distance
    return {'pos': pos, 'weight': weight, 'index': index}

# Перевод данных игры в нормальный для алгоритма вид
def generate_body(snake_body, cell_size):
    array = []

    for i in range(len(snake_body)):
        cell = snake_body[i]
        array.append([int(cell[0] / cell_size), int(cell[1] / cell_size), i])

    return array

def generate_array(body_array, cell_size, width, height):
    array_width = width / cell_size
    array_height = height / cell_size

    array = numpy.zeros(shape=(int(array_width), int(array_height)))

    for cell in body_array:
        array[cell[0], cell[1]] = -1
        #pygame.draw.rect(testWin, (0, 255, 0), pygame.Rect(cell[0] * cell_size + 10, cell[1] * cell_size + 10, 30, 30))
        #pygame.display.flip()

    return array