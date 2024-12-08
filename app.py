import pyxel
from pyxel import *
import math
import copy
import random


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"


def distance(a : Vector2, b : Vector2):
    return math.sqrt(((a.x - b.x) + (a.y - b.y))**2)


class Animation:
    def __init__(self, pos : Vector2, uv : Vector2, size : Vector2, n, speed = 1.0, inf = True):
        self.pos = pos
        self.uv = uv
        self.size = size
        self.n = n
        self.speed = speed
        self.animIndex = 0
        self.dir = 1
        self.inf = inf

    def is_last_frame(self):
        return self.animIndex == self.n - 1

    def play(self, pos : Vector2, dir):
        self.pos = pos
        self.dir = dir
        if pyxel.frame_count % (30 / self.speed) == 0:
            if self.is_last_frame():
                if self.inf:
                    self.animIndex = 0
                else:
                    self.animIndex = self.n - 1
            else:
                self.animIndex += 1

    def draw(self):
        blt(self.pos.x, self.pos.y, 0, self.uv.x + (self.animIndex * self.size.x), self.uv.y, self.size.x * self.dir, self.size.y, 5)


class Heart:
    def __init__(self, pos):
        self.pos = pos

    def interact(self, player):
        if self.pos.x < player.pos.x + 16 and self.pos.x + 16 > player.pos.x and self.pos.y < player.pos.y + 16 and self.pos.y + 16 > player.pos.y:
            player.take_heal(1)
            return True
        return False
        
    def draw(self):
        blt(self.pos.x, self.pos.y, 0, 48, 200, 16, 16, 5)


class Tile:
    def __init__(self, pos, w, h, dirX, color, trigger, layer, drawable):
        self.pos = pos
        self.w = w
        self.h = h
        self.color = color
        self.trigger = trigger
        self.layer = layer
        self.dirX = dirX
        self.drawable = drawable
    
    def draw(self):
        if self.drawable:
            rect(self.pos.x, self.pos.y, self.w, self.h, self.color)
        #blt(self.x, self.y, 0, self.tx, self.ty, self.w, self.h)


class Ennemy:
    def __init__(self, pos : Vector2, hp):
        self.pos = pos
        self.lastPos = Vector2(0, 0)
        self.w = 16
        self.h = 16
        self.hp = hp
        self.isDead = False
        self.hunting = True
        self.dmg = 0
        self.canAttack = True
        self.onGround = False
        self.dir = Vector2(1, 0)
        self.lookAt = 1
        self.attackRange = 10
        self.animations = [Animation(Vector2(self.pos.x, self.pos.y), Vector2(0, 136), Vector2(16, 16), 4, 5),  # WALK ANIM
                           Animation(Vector2(self.pos.x, self.pos.y), Vector2(0, 168), Vector2(16, 16), 5, 1.5),
                           Animation(Vector2(self.pos.x, self.pos.y), Vector2(128, 32), Vector2(16, 16), 8, 10)] # ATTACK ANIM
        self.currentAnim = 0

    def collision(self, x, y, tilemap, player):
        for tile in tilemap:
            if self.pos.x < tile.pos.x + tile.w and self.pos.x + 16 > tile.pos.x and self.pos.y < tile.pos.y + tile.h and self.pos.y + 12 > tile.pos.y:
                if tile.trigger is False:
                    if x > 0:
                        self.pos.x = tile.pos.x - 16
                        self.dir.x = 0
                    if x < 0:
                        self.pos.x = tile.pos.x + tile.w
                        self.dir.x = 0
                    if y > 0:
                        self.pos.y = tile.pos.y - 12
                        self.onGround = True
                        self.dir.y = 0
                    if y < 0:
                        self.pos.y = tile.pos.y + tile.h
                        self.dir.y = 0
                else:
                    if tile.layer is "JumpingSpace":
                        if x is tile.dirX:
                            if player.pos.y < self.pos.y:
                                if self.onGround:
                                    self.dir.y = -5.5
                                    self.pos.x += self.dir.x * 2

    def attack_player(self, player):
        if self.pos.x < player.pos.x + 16 and self.pos.x + 16 > player.pos.x and self.pos.y < player.pos.y + 16 and self.pos.y + 16 > player.pos.y:
            self.animations[self.currentAnim].play(Vector2(self.pos.x, self.pos.y), self.lookAt)
            if self.animations[self.currentAnim].is_last_frame() and self.canAttack:
                self.animations[self.currentAnim].animIndex = 0
                player.take_damage(2)
                self.canAttack = False
            else:
                self.canAttack = True

    def take_damage(self, dm):
        self.hp -= dm

    def update(self, tilemap, player, wave):
        if self.hp > 0:
            if not self.onGround:
                self.dir.y += 0.3
                if self.dir.y > 9.81:
                    self.dir.y = 9.81
            else:
                if not self.hunting and self.pos.y is not self.lastPos.y and not (self.pos.y - player.pos.y < 1 and self.pos.y - player.pos.y > -1):
                    self.hunting = True
                    
            if self.pos.x + self.w > 256 or self.pos.x < 0:
                self.dir.x = -self.dir.x
                self.lookAt = self.dir.x
                    
            if self.dir.x == 0:
                self.dir.x = 1
                self.lookAt = self.dir.x
                    
            if self.pos.y > 250:
                self.hp = 0
                
            print(self.hunting)
            if self.pos.y is not player.pos.y and self.hunting:
                if player.pos.x > self.pos.x:
                    self.dir.x = 1
                    self.lookAt = 1
                    self.lastPos = copy.deepcopy(self.pos)
                    self.hunting = False
                else:
                    self.dir.x = -1
                    self.lookAt = -1
                    self.lastPos = copy.deepcopy(self.pos)
                    self.hunting = False
            elif (self.pos.y - player.pos.y < 1 and self.pos.y - player.pos.y > -1)and not self.hunting:
                if player.pos.x - self.pos.x > 0:
                    self.dir.x = 1
                    self.lookAt = 1
                    self.currentAnim = 0
                elif distance(self.pos, player.pos) < 8:
                    self.dir.x = 0
                    self.currentAnim = 1
                    self.attack_player(player)
                else:
                    self.dir.x = -1
                    self.lookAt = -1
                    self.currentAnim = 0

            self.animations[self.currentAnim].play(Vector2(self.pos.x, self.pos.y), self.lookAt)

            self.pos.x += self.dir.x
            self.collision(self.dir.x, 0, tilemap, player)

            self.onGround = False
            self.pos.y += self.dir.y
            self.collision(0, self.dir.y, tilemap, player)
        else:
            self.currentAnim = 2
            self.animations[self.currentAnim].play(Vector2(self.pos.x, self.pos.y), self.lookAt)
            if self.animations[self.currentAnim].is_last_frame():
                wave.totalEnemies -= 1
                self.isDead = True

    def draw(self):
        self.animations[self.currentAnim].draw()


class Bullet:
    def __init__(self, pos_, dirX, player):
        self.pos = pos_
        self.startPos = player.pos
        self.d = dirX
        self.tooFar = False
        self.anim = Animation(pos_, Vector2(32, 8), Vector2(8, 8), 3, 10, False)

    def collision(self, ennemies):
        for e in ennemies:
            if self.pos.x < e.pos.x + 16 and self.pos.x + 8 > e.pos.x and self.pos.y < e.pos.y + 16 and self.pos.y + 8 > e.pos.y:
                e.take_damage(1)
                return True
        return False
        
    def update(self):
        self.pos.x += self.d * 7
        self.anim.play(self.pos, self.d)
        if math.sqrt((self.pos.x - self.startPos.x)**2) > 260:
            self.tooFar = True

    def draw(self):
        self.anim.draw()


class Bullet2:
    def __init__(self, pos_, dirX, player):
        self.pos = pos_
        self.startPos = player.pos
        self.d = dirX
        self.tooFar = False
        self.anim = Animation(pos_, Vector2(32, 32), Vector2(16, 16), 3, 2, False)

    def collision(self, ennemies):
        for e in ennemies:
            if self.pos.x < e.pos.x + 16 and self.pos.x + 16 > e.pos.x and self.pos.y < e.pos.y + 16 and self.pos.y + 16 > e.pos.y:
                if self.anim.is_last_frame():
                    e.take_damage(10)
                else:
                    e.take_damage(5)
                return True
        return False

    def update(self):
        self.pos.x += self.d * 2
        self.anim.play(self.pos, self.d)
        if math.sqrt((self.pos.x - self.startPos.x) ** 2) > 260:
            self.tooFar = True

    def draw(self):
        self.anim.draw()


class Player:
    def __init__(self, pos):
        self.pos = pos
        self.lastY = pos.y
        self.w = 16
        self.h = 16
        self.speed = 3
        self.onGround = False
        self.dir = Vector2(0, 0)
        self.bullets = []
        self.lookAt = 1
        self.hp = 10
        self.max_hp = 3
        self.isDead = False
        self.animations = [Animation(Vector2(self.pos.x, self.pos.y), Vector2(0, 8), Vector2(16, 16), 2, 2),              # IDLE ANIM
                           Animation(Vector2(self.pos.x, self.pos.y), Vector2(0, 24), Vector2(16, 16), 2, 10),            # WALK ANIM
                           Animation(Vector2(self.pos.x, self.pos.y), Vector2(0, 88), Vector2(16, 16), 5, 2, False),  # DEATH ANIM
                           Animation(Vector2(self.pos.x, self.pos.y), Vector2(0, 104), Vector2(16, 16), 3, 2, False)] # WIN ANIM
        self.currentAnim = 0

        self.shoot = False

        self.canShoot2 = False

    def collision(self, x, y, tilemap):
        for tile in tilemap:
            if self.pos.x < tile.pos.x + tile.w and self.pos.x + 16 > tile.pos.x and self.pos.y < tile.pos.y + tile.h and self.pos.y + 12 > tile.pos.y:
                if tile.trigger is False:
                    if x > 0:
                        self.pos.x = tile.pos.x - 16
                        self.dir.x = 0
                    if x < 0:
                        self.pos.x = tile.pos.x + tile.w
                        self.dir.x = 0
                    if y > 0:
                        self.pos.y = tile.pos.y - 12
                        self.onGround = True
                        self.dir.y = 0
                    if y < 0:
                        self.pos.y = tile.pos.y + tile.h
                        self.dir.y = 0

    def take_damage(self, dm):
        self.hp -= dm

    def take_heal(self, hp):
        self.hp += hp

    def update(self, tilemap, enemies):
        if self.hp > 0:
            if btn(KEY_SPACE) and self.onGround:
                self.dir.y = -5
            if not self.onGround:
                self.dir.y += 0.3
                if self.dir.y > 9.81:
                    self.dir.y = 9.81

            if self.pos.y > 250:
                self.hp = 0

            if not self.canShoot2:
                if pyxel.frame_count % 90 == 0:
                    self.canShoot2 = True

            if not self.shoot:
                if pyxel.frame_count % 5 == 0:
                    self.shoot = True

            if btn(KEY_A) and self.shoot:
                if self.lookAt == -1:
                    self.bullets.append(Bullet(Vector2(self.pos.x - 8, self.pos.y + 3), self.lookAt, self))
                else:
                    self.bullets.append(Bullet(Vector2(self.pos.x + 16, self.pos.y + 3), self.lookAt, self))
                self.shoot = False

            if btnp(KEY_E) and self.canShoot2:
                if self.lookAt == -1:
                    self.bullets.append(Bullet2(Vector2(self.pos.x - 8, self.pos.y + 3), self.lookAt, self))
                else:
                    self.bullets.append(Bullet2(Vector2(self.pos.x + 16, self.pos.y + 3), self.lookAt, self))
                self.canShoot2 = False

            if self.bullets:
                for b in self.bullets:
                    if b.tooFar:
                        self.bullets.remove(b)
                    if b.collision(enemies):
                        self.bullets.remove(b)
                    b.update()
            
            if self.pos.x + self.w >= 256 or self.pos.x <= 0:
                if self.dir.x < 0:
                    self.pos.x = 0
                if self.dir.x > 0:
                    self.pos.x = 256 - self.w
                
            if btn(KEY_D):
                    self.dir.x = 1
                    self.lookAt = 1
                    self.w = 16
                    self.currentAnim = 1
            elif btn(KEY_Q):
                self.dir.x = -1
                self.lookAt = -1
                self.w = -16
                self.currentAnim = 1
            else:
                self.dir.x = 0
                self.currentAnim = 0

            self.animations[self.currentAnim].play(Vector2(self.pos.x, self.pos.y), self.lookAt)

            self.pos.x += self.dir.x * self.speed
            self.collision(self.dir.x * self.speed, 0, tilemap)

            self.pos.y += self.dir.y
            self.onGround = False
            self.collision(0, self.dir.y * self.speed, tilemap)
        else:
            self.currentAnim = 2
            self.animations[self.currentAnim].play(Vector2(self.pos.x, self.pos.y), self.lookAt)
            if self.animations[self.currentAnim].is_last_frame():
                self.isDead = True

    def draw(self):
        self.animations[self.currentAnim].draw()
        for b in self.bullets:
            b.draw()
        for h in range(self.hp):
            blt(h * 5, 8, 0, 48, 200, 16, 16, 5)


class Wave:
    def __init__(self, count, speed, ehp):
        self.enemiesCount = count
        self.totalEnemies = copy.deepcopy(count)
        self.enemies = []
        self.spawnSpeed = speed
        self.isInit = False
        self.spawnPoints = [
            Vector2(5, 190),
            Vector2(227, 190)
        ]
        self.itemsSpawnPoints = [
            Vector2(17, 154),
            Vector2(223, 154),
            Vector2(117.5, 134)
        ]
        self.items = []
        self.spawnPointIndex = 0
        self.waitTime = 5
        self.enemiesHp = ehp

    def update(self, map, player):
        print(len(self.items))
        self.items_interaction(player)
        if self.enemiesCount > 0:
            if not self.isInit:
                self.spawn_items()
                self.isInit = True
            if pyxel.frame_count % (30 / self.spawnSpeed) == 0:
                self.enemies.append(Ennemy(copy.deepcopy(self.spawnPoints)[self.spawnPointIndex], self.enemiesHp))
                self.enemiesCount -= 1
                if self.spawnPointIndex == len(self.spawnPoints) - 1:
                    self.spawnPointIndex = 0
                else:
                    self.spawnPointIndex += 1
        else:
            self.isInit = False
        for e in self.enemies:
            e.update(map, player, self)
            if e.isDead:
                self.enemies.remove(e)
            
    def spawn_items(self):
        for i in range(3):
            heart = Heart(self.itemsSpawnPoints[random.randint(0, len(self.itemsSpawnPoints))])
            self.items.append(heart)
        
    def items_interaction(self, player):
        for i in self.items:
            if i.interact(player):
                self.items.remove(i)
                

    def next_wave(self):
        return self.totalEnemies == 0

    def draw(self):
        for i in self.items:
            i.draw()
        for e in self.enemies:
            e.draw()
            
            
class GameScene:
    def __init__(self):
        self.player = Player(Vector2(100, 134))
        self.map = [
            Tile(Vector2(0, 206), 256, 16, 0, 5, False, "Ground", True),
            Tile(Vector2(0, 170), 50, 8, 0, 5, False, "Ground", True),
            Tile(Vector2(206, 170), 50, 8, 0, 5, False, "Ground", True),
            Tile(Vector2(80, 150), 95, 8, 0, 5, False, "Ground", True),
            Tile(Vector2(50, 190), 16, 16, -1, 6, True, "JumpingSpace", False),
            Tile(Vector2(34, 154), 16, 16, 1, 6, True, "JumpingSpace", False),
            Tile(Vector2(190, 190), 16, 16, 1, 6, True, "JumpingSpace", False),
            Tile(Vector2(206, 154), 16, 16, -1, 6, True, "JumpingSpace", False)
        ]

        self.waves = [
            Wave(1, 0.5, 5),
            Wave(10, 0.5, 10),
            Wave(20, 0.5, 20),
            Wave(30, 0.5, 25),
            Wave(40, 0.5, 30)
        ]
        self.currentWave = 0
        
    def update(self):
        if not self.player.isDead:
            self.player.update(self.map, self.waves[self.currentWave].enemies)
            self.waves[self.currentWave].update(self.map, self.player)
            if self.waves[self.currentWave].next_wave():
                self.waves[self.currentWave].items = []
                self.currentWave += 1
            if self.currentWave > len(self.waves) - 1:
                self.win()
        else:
            self.game_over()

    def game_over(self):
        pass

    def win(self):
        pass
        
    def draw(self):
        if not self.player.isDead:
            cls(3)
            for tile in self.map:
                tile.draw()
            self.player.draw()
            self.waves[self.currentWave].draw()

            text(0, 241, f"Wave : {self.currentWave}", 7)
            text(0, 251, f"Enemies : {self.waves[self.currentWave].totalEnemies}", 7)

        else:
            cls(0)
            text(100, 100, "Game Over", 7)


class Game:
    def __init__(self):
        init(256, 256)
        load("3.pyxres")
        self.player = Player(Vector2(100, 134))
        self.map = [
            Tile(Vector2(0, 206), 256, 16, 0, 5, False, "Ground", True),
            Tile(Vector2(0, 170), 50, 8, 0, 5, False, "Ground", True),
            Tile(Vector2(206, 170), 50, 8, 0, 5, False, "Ground", True),
            Tile(Vector2(80, 150), 95, 8, 0, 5, False, "Ground", True),
            Tile(Vector2(50, 190), 16, 16, -1, 6, True, "JumpingSpace", False),
            Tile(Vector2(34, 154), 16, 16, 1, 6, True, "JumpingSpace", False),
            Tile(Vector2(190, 190), 16, 16, 1, 6, True, "JumpingSpace", False),
            Tile(Vector2(206, 154), 16, 16, -1, 6, True, "JumpingSpace", False)
        ]
    
        self.waves = [
            Wave(1, 0.5, 5),
            Wave(10, 0.5, 10),
            Wave(20, 0.5, 20),
            Wave(30, 0.5, 25),
            Wave(40, 0.5, 30)
        ]
        self.currentWave = 0
        run(self.update, self.draw)
        
    def update(self):
        if not self.player.isDead:
            self.player.update(self.map, self.waves[self.currentWave].enemies)
            self.waves[self.currentWave].update(self.map, self.player)
            if self.waves[self.currentWave].next_wave():
                self.waves[self.currentWave].items = []
                self.currentWave += 1
            if self.currentWave > len(self.waves) - 1:
                self.win()
        else:
            self.game_over()

    def game_over(self):
        pass

    def win(self):
        pass
        
    def draw(self):
        if not self.player.isDead:
            cls(3)
            for tile in self.map:
                tile.draw()
            self.player.draw()
            self.waves[self.currentWave].draw()

            text(0, 241, f"Wave : {self.currentWave}", 7)
            text(0, 251, f"Enemies : {self.waves[self.currentWave].totalEnemies}", 7)

        else:
            cls(0)
            text(100, 100, "Game Over", 7)



Game()