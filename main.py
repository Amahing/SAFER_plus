import random
import tab_and_mat # таблиці і матриці


def multiply_matrices(matrix1, matrix2):
    # Перевіряємо, що кількість стовпців першої матриці дорівнює кількості рядків у другій матриці
    if len(matrix1[0]) != len(matrix2):
        raise ValueError(
            "Неможливо помножити матриці. Кількість стовпців першої матриці"
            "має дорівнювати кількості рядків другої матриці.")

    result = [[0 for _ in range(len(matrix2[0]))] for _ in range(len(matrix1))]

    for i in range(len(matrix1)):
        for j in range(len(matrix2[0])):
            for k in range(len(matrix2)):
                result[i][j] += matrix1[i][k] * matrix2[k][j]
                result[i][j] %= 256  # Взяття по модулю 256

    return [element for row in result for element in row]


def main():
    print("Проводимо генерацію 128-бітного ключа:")
    my_key = [[0] * 16 for _ in range(18)]  # Створення списку з 17 підписків по 16 елементів.

    my_first_key = [None] * 17
    for i in range(16):
        my_first_key[i] = random.randint(0, 255)
    # print("Створений 1-й ключ", my_first_key)
    my_key[0][:16] = my_first_key[:16]
    # print("my_key0", my_key)


    result = 0
    for i in range(16):
        result ^= my_first_key[i]  # Розраховуємо додатковий байт
    my_first_key[16] = result
    # print("\nЗ додатковим байтом: ", my_first_key)

    for i in range(1, 17):
        my_first_key = my_first_key[3:] + my_first_key[:3]  # Циклічий зсув на 3 вліво

        for x in range(16):
            my_key[i][x] = (my_first_key[(i + x) % 16] + tab_and_mat.constants_for_generate_key[i][x]) % 256
        # print(f"Після операції складання, раунду шифрування №{i}, ключ:{my_key[i]}")

    # for x in my_key:
    #    print(x)

    print(my_key)

    ########################
    ### КЛЮЧ ЗГЕНЕРОВАНО ###
    ########################

    """ПОЧАТОК ШИФРУВАННЯ"""

    text = list(input("\nНапишіть текст англійською мовою який потрібно зашифрувати: "))

    while len(text) % 16 != 0:
        text.append(" ")  # Заповнення відкритого тексту символами пробілу, щоб кількість
        # символів була кратна 16

    # list_inp_numbers це вхідний текст у вигляді чисел
    list_inp_numbers = [ord(char) for char in text] # перетворення в ASCII
    print("Відкритий текст (після перетворення за ASCII):", list_inp_numbers)


    amount_blocks = len(list_inp_numbers) // 16
    # print(f"Кількість блоків {amount_blocks}")

    counter = 0  # Лічильник пройденних блоків для шифрування
    ciphertext_int = []  # Створення списку ciphertext_int в якій будуть поміщуватися зашифровані символи

    for y in range(amount_blocks):  # РОЗБИВАЄМО МАСИВ
        block_for_encrypt = []
        for j in range(16):
            block_for_encrypt.append(list_inp_numbers[16 * counter + j])

        for i in range(1, 9):  # ШИФРУВАННЯ, для 8 раундів шифрування
            for x in range(1, 17):  # 1 step
                if x in [1, 4, 5, 8, 9, 12, 13, 16]:
                    block_for_encrypt[x - 1] = block_for_encrypt[x - 1] ^ my_key[2 * i - 1][x - 1]
                else:
                    block_for_encrypt[x - 1] = (block_for_encrypt[x - 1] + my_key[2 * i - 1][x - 1]) % 256
            print(f"i={i}, step1, T:{block_for_encrypt}")

            for x in range(1, 17):  # 2 step
                if x in [1, 4, 5, 8, 9, 12, 13, 16]:
                    block_for_encrypt[x - 1] = tab_and_mat.arrE[tab_and_mat.arrE.index(block_for_encrypt[x - 1])]
                else:
                    block_for_encrypt[x - 1] = tab_and_mat.arrL[tab_and_mat.arrL.index(block_for_encrypt[x - 1])]
            print(f"i={i}, step2, T:{block_for_encrypt}")

            for x in range(1, 17):  # 3 step
                if x in [1, 4, 5, 8, 9, 12, 13, 16]:
                    block_for_encrypt[x - 1] = (block_for_encrypt[x - 1] + my_key[2 * i][x - 1]) % 256
                else:
                    block_for_encrypt[x - 1] = block_for_encrypt[x - 1] ^ my_key[2 * i][x - 1]
            print(f"i={i}, step3, T:{block_for_encrypt}")

            # 4 step
            for_matrix_block = [block_for_encrypt[:16], block_for_encrypt[:16]]
            result = multiply_matrices(for_matrix_block, tab_and_mat.matrix_for_encrypt)
            block_for_encrypt = result[:16]
            print(f"i={i}, step4, T:{block_for_encrypt}")

            for x in range(1, 17):  # Заключне перетворення
                if x in [1, 4, 5, 8, 9, 12, 13, 16]:
                    block_for_encrypt[x - 1] = block_for_encrypt[x - 1] ^ my_key[17][x - 1]
                else:
                    block_for_encrypt[x - 1] = (block_for_encrypt[x - 1] + my_key[17][x - 1]) % 256

        for x in range(16):
            ciphertext_int.append(block_for_encrypt[x])

        counter += 1

    print("Шифротекст (байтами):", ciphertext_int, "\n\n\n")
    #print("Шифротекст:", ' '.join(map(str, ciphertext_int)))

    """ПОЧАТОК ДЕШИФРУВАННЯ"""

    counter = 0
    decrypt_finish = []

    for y in range(amount_blocks):  # РОЗБИВАЄМО МАСИВ
        block_for_decrypt = []
        for j in range(16):
            block_for_decrypt.append(ciphertext_int[16 * counter + j])
        for i in range(8, 0, -1):  # ДЕШИФРУВАННЯ, для 8 раундів
            # 0 step - import
            print(f"i={i}, step0, T:{block_for_decrypt}")

            for x in range(1, 17):  # Зворотне заключне перетворення
                if x in [1, 4, 5, 8, 9, 12, 13, 16]:
                    block_for_decrypt[x - 1] = block_for_decrypt[x - 1] - my_key[17][x - 1]
                else:
                    block_for_decrypt[x - 1] = (block_for_decrypt[x - 1] ^ my_key[17][x - 1]) % 256

            # 1 step
            for_matrix_block = [block_for_decrypt[:16], block_for_decrypt[:16]]
            result = multiply_matrices(for_matrix_block, tab_and_mat.matrix_for_decrypt)
            block_for_decrypt = result[:16]
            print(f"i={i}, step1, T:{block_for_decrypt}")

            for x in range(1, 17):  # 2 step
                if x in [1, 4, 5, 8, 9, 12, 13, 16]:
                    block_for_decrypt[x - 1] = (block_for_decrypt[x - 1] - my_key[2 * i][x - 1]) % 256
                else:
                    block_for_decrypt[x - 1] = block_for_decrypt[x - 1] ^ my_key[2 * i][x - 1]
            print(f"i={i}, step2, T:{block_for_decrypt}")

            for x in range(1, 17):  # 3 step
                if x in [1, 4, 5, 8, 9, 12, 13, 16]:
                    block_for_decrypt[x - 1] = tab_and_mat.arrL[tab_and_mat.arrL.index(block_for_decrypt[x - 1])]
                else:
                    block_for_decrypt[x - 1] = tab_and_mat.arrE[tab_and_mat.arrE.index(block_for_decrypt[x - 1])]
            print(f"i={i}, step3, T:{block_for_decrypt}")

            for x in range(1, 17):  # 4 step
                if x in [1, 4, 5, 8, 9, 12, 13, 16]:
                    block_for_decrypt[x - 1] ^= my_key[2 * i - 1][x - 1]
                else:
                    block_for_decrypt[x - 1] = (block_for_decrypt[x - 1] - my_key[2 * i - 1][x - 1]) % 256
            print(f"i={i}, step4, T:{block_for_decrypt}")

        for x in range(16):
            decrypt_finish.append(block_for_decrypt[x])
        counter += 1

    print("Дешифрований текст (байтами):", decrypt_finish)
    decrypted_text = ''.join([chr(char) for char in decrypt_finish])
    print("Дешифрований текст (після перетворення за ASCII):", decrypted_text)


if __name__ == "__main__":
    main()
    b = input()
